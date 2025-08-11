from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name="home"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_item/', views.update_item, name='update_item'),
    path('add-to-cart-then-checkout/<int:product_id>/', views.add_to_cart_then_checkout, name='add_to_cart_then_checkout'),
    path('checkout/orders_placed/', views.orders_placed_view, name='orders_placed'),  # Đảm bảo URL này được định nghĩa
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    # Trong urls.py
path('product/<int:product_id>/', views.product_detail, name='product_detail'),  # Đảm bảo tham số đúng với product_id
path('product/<int:product_id>/review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
path('product/<int:product_id>/review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
path('product/<int:product_id>/review/add/', views.add_review, name='add_review'),
path('khuyen-mai/', views.promotion_products, name='promotion_products'),
path('tin-cong-nghe/', views.tech_news, name='tech_news'),
path('tin-cong-nghe/<slug:slug>/', views.tech_news_detail, name='tech_news_detail'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
