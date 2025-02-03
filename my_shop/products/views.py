from django.shortcuts import render
from .models import Product

def home(request):
    products = Product.objects.all()  # Получаем все товары из базы данных
    return render(request, 'products/home.html', {'products': products})