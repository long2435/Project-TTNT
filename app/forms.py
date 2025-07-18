from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from .models import ProductReview


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email','first_name', 'last_name', 'password1', 'password2']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']


# Form cập nhật thông tin người dùng (User model)
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1, 'max': 5, 'class': 'form-control', 'placeholder': 'Chọn số sao từ 1 đến 5'
            }),
            'comment': forms.Textarea(attrs={
                'rows': 3, 'class': 'form-control', 'placeholder': 'Viết nhận xét của bạn ở đây...'
            }),
        }
        labels = {
            'rating': 'Số sao',
            'comment': 'Nhận xét',
        }
