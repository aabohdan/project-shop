from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product, ProductImage, SubCategory
from .models import Profile
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import re




class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="Электронная почта", 
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Введите ваш адрес электронной почты.'})
    )
    first_name = forms.CharField(
        label="Имя", 
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Введите ваше имя.'})
    )
    last_name = forms.CharField(
        label="Фамилия", 
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Введите вашу фамилию.'})  
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Имя пользователя"
        self.fields['username'].widget.attrs.update({'placeholder': 'Введите уникальное имя пользователя.'}) 
        self.fields['password1'].label = "Пароль"
        self.fields['password1'].widget.attrs.update({'placeholder': 'Введите пароль.'})  
        self.fields['password2'].label = "Подтверждение пароля"
        self.fields['password2'].widget.attrs.update({'placeholder': 'Введите пароль еще раз для подтверждения.'})  
        
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return [single_file_clean(data, initial)]

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'main_category', 'subcategory', 'sizes', 'colors', 'composition']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'main_category': forms.Select(attrs={'class': 'form-select'}),
            'subcategory': forms.Select(attrs={'class': 'form-select'}),
            'sizes': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'colors': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'composition': forms.SelectMultiple(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.fields['subcategory'].queryset = SubCategory.objects.none()
        
        if 'main_category' in self.data:
            try:
                main_category_id = int(self.data.get('main_category'))
                self.fields['subcategory'].queryset = SubCategory.objects.filter(
                    main_category_id=main_category_id
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['subcategory'].queryset = self.instance.main_category.subcategory_set.all()
                
class ProductImageForm(forms.ModelForm):
    images = MultipleFileField(required=False)

    class Meta:
        model = ProductImage
        fields = []
        
class CheckoutForm(forms.Form):
    name = forms.CharField(label='ФИО', max_length=100, required=True)
    phone = forms.CharField(label='Телефон', max_length=20, required=True)
    address = forms.CharField(
        label='Адрес доставки',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True
    )
    notes = forms.CharField(
        label='Комментарий к заказу',
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False
    )
    
    
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': 'Логин',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Электронная почта',
        }
        help_texts = {
            'username': 'Обязательное поле. Не более 150 символов. Только буквы, цифры и @/./+/-/_',
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'birth_date', 'avatar']
        labels = {
            'phone': 'Телефон',
            'address': 'Адрес',
            'birth_date': 'Дата рождения',
            'avatar': 'Аватар',
        }
        widgets = {
            'phone': forms.TextInput(attrs={
                'placeholder': '+375 (XX) XXX-XX-XX',
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Введите ваш полный адрес',
                'class': 'form-control'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }, format='%Y-%m-%d'),
        }
        help_texts = {
            'phone': 'Формат: +375 (XX) XXX-XX-XX',
            'birth_date': 'Выберите дату в календаре',
        }