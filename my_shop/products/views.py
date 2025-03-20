from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm  
from django.contrib import messages
from .models import Product, ProductImage
from .forms import ProductForm, ProductImageForm

def home(request):
    return render(request, 'products/home.html')

def baby(request):
    return render(request, 'products/baby.html')

def boys(request):
    return render(request, 'products/boys.html')

def girls(request):
    return render(request, 'products/girls.html')

def shoes(request):
    return render(request, 'products/shoes.html')

def accessories(request):
    return render(request, 'products/accessories.html')

def delpay(request):
    return render(request, 'products/delpay.html')

def basket(request):
    return render(request, 'products/basket.html')

@login_required
def autf(request):
    return render(request, 'products/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт {username} успешно создан! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def is_vendor(user):
    return user.groups.filter(name='Vendors').exists()

@login_required
@user_passes_test(is_vendor)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            return redirect('add_product_image', product_id=product.id)  # Перенаправление на добавление изображений
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})

@login_required
@user_passes_test(is_vendor)
def add_product_image(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.product = product
            image.save()
            return redirect('add_product_image', product_id=product.id)  # Остаемся на той же странице для добавления еще изображений
    else:
        form = ProductImageForm()
    return render(request, 'products/add_product_image.html', {'form': form, 'product': product})