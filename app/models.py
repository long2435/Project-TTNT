from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify




# Danh mục sản phẩm 
class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)  # Thêm dòng này

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Tạo slug tự động từ tên
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


# Customer liên kết với User
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=False)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name

# Sản phẩm
class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=False)
    image = models.ImageField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Xóa discount_end và các hàm xử lý thời gian

    def is_discount(self):
        """Kiểm tra xem sản phẩm có khuyến mãi hay không."""
        return self.discount_price is not None and self.discount_price < self.price

    def get_final_price(self):
        """Trả về giá sau khi áp dụng khuyến mãi (nếu có)."""
        if self.is_discount():
            return float(self.discount_price)
        return float(self.price)

    def __str__(self):
        return self.name

    @property
    def ImageURL(self):
        try:
            return self.image.url
        except:
            return ''

    @property
    def current_price(self):
        return float(self.discount_price) if self.is_discount() else float(self.price)



# Đánh giá sản phẩm
class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)  # Từ 1 đến 5 sao
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.product.name} ({self.rating}⭐)'



# Đơn hàng
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_order = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

# Sản phẩm trong đơn hàng
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    price = models.FloatField(null=True, blank=True)  # Lưu giá tại thời điểm thêm vào giỏ hàng

    @property
    def get_total(self):
        unit_price = self.price if self.price is not None else self.product.get_final_price()
        return unit_price * self.quantity
    
    @property
    def get_total(self):
        return self.product.current_price * self.quantity


# Địa chỉ giao hàng
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    mobile = models.CharField(max_length=10, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.address)

# Hàm đặt đường dẫn lưu avatar
def user_avatar_path(instance, filename):
    return f'avatars/user_{instance.user.id}/{filename}'

# Hồ sơ người dùng
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def get_total_price(self):
        return sum(product.price for product in self.products.all())
    
class TechNews(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)  # Dùng để tạo đường dẫn đẹp
    image = models.ImageField(upload_to='news_images/')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title