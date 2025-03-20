from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product, ProductImage


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
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'categories', 'sizes', 'colors']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Название товара"
        self.fields['description'].label = "Описание товара"
        self.fields['price'].label = "Цена"
        self.fields['categories'].label = "Категории"
        self.fields['sizes'].label = "Размеры"
        self.fields['colors'].label = "Цвета"
        
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].label = "Изображение товара"
        

        
