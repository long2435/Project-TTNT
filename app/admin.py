from django.contrib import admin
from .models import TechNews
from .models import (
    Customer, Product, Order, OrderItem,
    ShippingAddress, UserProfile, Category
)

# Hiển thị sản phẩm trong phần danh mục
class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    fields = ['name', 'price', 'image', 'is_featured', 'category']  # Thêm is_featured

# Tùy chỉnh hiển thị danh mục
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductInline]

# Tùy chỉnh hiển thị sản phẩm
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'is_featured')  # Thêm is_featured
    list_filter = ('category', 'is_featured')  # Thêm is_featured
    list_editable = ('is_featured',)  # Thêm is_featured
    prepopulated_fields = {'slug': ('name',)}  # Tự động tạo slug từ tên sản phẩm

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount_price', 'is_featured', 'category')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'category__name')  

# Đăng ký các model vào admin
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(UserProfile)
admin.site.register(TechNews)