from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Product, Cart
from .models import Category
from .models import ProductReview
from .forms import ProductReviewForm
from .models import TechNews
from django.core.paginator import Paginator



def home(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    products = Product.objects.filter(is_featured=True)

    if query:
        products = products.filter(name__icontains=query)

    if category_slug:
        try:
            category = Category.objects.get(slug=category_slug)
            products = products.filter(category=category)
        except Category.DoesNotExist:
            pass

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    categories = Category.objects.all()

    # 👉 Phân trang: mỗi trang 10 sản phẩm
    paginator = Paginator(products, 12)  # Thay số 10 bằng số sản phẩm mỗi trang bạn muốn
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)



    context = {
        'page_obj': page_obj,  # sử dụng trong template
        'categories': categories,
        'query': query,
        'category_filter': category_slug,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'app/home.html', context)



# Giỏ hàng
def cart(request):
    if request.user.is_authenticated:
        customer, _ = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()

        # Tính tổng giỏ hàng dựa trên giá của OrderItem
        total = sum(item.get_total for item in items)
        context = {'items': items, 'order': order, 'total': total}
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        context = {'items': items, 'order': order}
    return render(request, 'app/cart.html', context)

# View xoá sản phẩm khỏi giỏ hàng
@login_required
@csrf_exempt
def delete_cart_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('productId')

        customer = Customer.objects.get(user=request.user)
        order = Order.objects.get(customer=customer, complete=False)

        try:
            order_item = OrderItem.objects.get(order=order, product_id=product_id)
            order_item.delete()
            return JsonResponse({'message': 'Đã xóa sản phẩm khỏi giỏ hàng.'}, status=200)
        except OrderItem.DoesNotExist:
            return JsonResponse({'error': 'Sản phẩm không tồn tại trong giỏ hàng.'}, status=404)

    return JsonResponse({'error': 'Phương thức không hợp lệ'}, status=400)

# Thanh toán
def checkout(request):
    if request.user.is_authenticated:
        customer, _ = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()

        if request.method == 'POST':
            data = request.POST
            try:
                total = float(data.get('total', 0))
            except ValueError:
                total = 0

            cart_total = order.get_cart_total

            if round(total, 2) == round(cart_total, 2):
                order.complete = True
                order.save()

                ShippingAddress.objects.create(
                    customer=customer,
                    order=order,
                    address=data.get('address'),
                    city=data.get('city'),
                    state=data.get('state'),
                    mobile=data.get('mobile'),
                )

                payment_method = data.get('payment_method')

                if payment_method == 'cod':
                    messages.success(request, "Cảm ơn bạn đã mua hàng! Đơn hàng sẽ được giao sớm.")
                    return redirect('orders_placed')
                elif payment_method == 'bank':
                    messages.success(request, "Cảm ơn bạn đã mua hàng! Vui lòng chuyển khoản theo hướng dẫn bên dưới.")
                    return render(request, 'app/bank_transfer.html', {'order': order})
            else:
                messages.error(request, "Tổng thanh toán không khớp. Vui lòng thử lại.")

        context = {'items': items, 'order': order}
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        context = {'items': items, 'order': order}
    return render(request, 'app/checkout.html', context)


# Đăng ký
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(user=user, name=user.username)
            messages.success(request, "Đăng ký thành công. Bạn có thể đăng nhập.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'app/register.html', {'form': form})

# Đăng nhập
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Sai tên đăng nhập hoặc mật khẩu.")
    return render(request, 'app/login.html')

# Đăng xuất
def logout_view(request):
    logout(request)
    return redirect('login')

# Trang cá nhân
@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            full_name = request.POST.get('full_name', '').strip()
            if full_name:
                parts = full_name.split(' ', 1)
                request.user.first_name = parts[0]
                request.user.last_name = parts[1] if len(parts) > 1 else ''

            request.user.email = request.POST.get('email', '')
            request.user.save()

            profile.phone = request.POST.get('phone', '')
            profile.birth_date = request.POST.get('birth_date') or None
            profile.gender = request.POST.get('gender', '')
            profile.address = request.POST.get('address', '')
            profile.bio = request.POST.get('bio', '')
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            profile.save()

            messages.success(request, 'Thông tin cá nhân đã được cập nhật.')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile
    }
    return render(request, 'app/profile.html', context)


# Thêm vào giỏ hàng
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    customer, _ = Customer.objects.get_or_create(user=request.user)
    order, _ = Order.objects.get_or_create(customer=customer, complete=False)

    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
    if not created:
        order_item.quantity += 1
        order_item.save()

    # Lưu giá giảm vào OrderItem nếu có
    order_item.price = product.get_final_price()
    order_item.save()

    messages.success(request, f'Đã thêm "{product.name}" vào giỏ hàng.')
    return redirect('cart')

# Cập nhật giỏ hàng bằng Ajax
# Cập nhật giỏ hàng với số lượng từ input
@csrf_exempt
@login_required
def update_item(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']
    quantity = data.get('quantity')  # quantity chỉ có khi action là 'update'

    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        order_item.quantity += 1
        order_item.save()

    elif action == 'remove':
        order_item.quantity -= 1
        if order_item.quantity <= 0:
            order_item.delete()
        else:
            order_item.save()

    elif action == 'update':
        try:
            quantity = int(quantity)
            if quantity > 0:
                order_item.quantity = quantity
                order_item.save()
            else:
                order_item.delete()
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid quantity'}, status=400)

    return JsonResponse({'message': 'Item updated'}, status=200)



@login_required
def orders_placed_view(request):
    customer = Customer.objects.get(user=request.user)
    orders = Order.objects.filter(customer=customer, complete=True).order_by('-date_order')

    for order in orders:
        order.ordered_items = order.orderitem_set.select_related('product').order_by('product__id')

    return render(request, 'app/orders_placed.html', {'orders': orders})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    context = {
        'category': category,
        'products': products
    }
    return render(request, 'app/category_products.html', context)

def categories_context(request):
    return {'categories': Category.objects.all()}


# Chi tiết sản phẩm
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.select_related('user').order_by('-created_at')
    review_form = ProductReviewForm() if request.user.is_authenticated else None

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'final_price': product.get_final_price(),  # Truyền giá giảm (nếu có)
    }
    return render(request, 'app/product_detail.html', context)

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductReviewForm()
    return render(request, 'product/add_review.html', {'form': form, 'product': product})


@login_required
def edit_review(request, product_id, review_id):
    product = get_object_or_404(Product, id=product_id)
    review = get_object_or_404(ProductReview, id=review_id, product=product, user=request.user)
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật đánh giá thành công.")
            return redirect('product_detail', product_id=product.id)
        else:
            messages.error(request, "Dữ liệu không hợp lệ.")
    else:
        form = ProductReviewForm(instance=review)
    
    return render(request, 'app/edit_review.html', {
        'form': form,
        'product': product,
        'review': review,
    })



#Ví dụ về cách định nghĩa view add_to_cart_then_checkout
def add_to_cart_then_checkout(request, product_id):
    product = Product.objects.get(id=product_id)
    # Thêm sản phẩm vào giỏ hàng (giả sử bạn có một mô hình giỏ hàng)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.products.add(product)
    # Chuyển hướng đến trang thanh toán
    return redirect('checkout')

def delete_review(request, product_id, review_id):
    review = get_object_or_404(ProductReview, id=review_id, product_id=product_id, user=request.user)
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Đã xoá đánh giá thành công.')
        return redirect('product_detail', product_id=product_id)

    messages.warning(request, 'Bạn cần gửi yêu cầu POST để xoá.')
    return redirect('product_detail', product_id=product_id)


def promotion_products(request):
    products = Product.objects.filter(discount_price__isnull=False, discount_price__lt=models.F('price'))
    return render(request, 'app/promotion.html', {'products': products})

def tech_news(request):
    news_list = TechNews.objects.all().order_by('-created_at')
    return render(request, 'app/tech_news.html', {'news_list': news_list})

def tech_news_detail(request, slug):
    news = get_object_or_404(TechNews, slug=slug)
    return render(request, 'app/tech_news_detail.html', {'news': news})