from django.shortcuts import render
from .models import Product
from django.contrib.auth.decorators import login_required

def home(request):
    products = Product.objects.all()  # Получаем все товары из базы данных
    return render(request, 'products/home.html', {'products': products})

@login_required
def home(request):
    return render(request, 'products/home.html')