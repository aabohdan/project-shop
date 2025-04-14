from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, get_object_or_404, redirect  
from .models import Product, MainCategory, ProductImage, SubCategory, Basket, Order, OrderItem, Profile, Size, Color
from .forms import CustomUserCreationForm, ProductForm, UserUpdateForm, ProfileUpdateForm, CheckoutForm
from django.db.models import Q, Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models.functions import Lower
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.urls import reverse 


@login_required
def profile(request):
    """Отображение профиля пользователя (только чтение)"""
    return render(request, 'products/profile.html', {
        'user': request.user
    })

@login_required
def profile_edit(request):
    """Редактирование профиля пользователя"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'products/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def delivery_payment(request):
    return render(request, 'products/delivery_payment.html')

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

def logout_view(request):
    return LogoutView.as_view()(request)

def is_vendor(user):
    return user.groups.filter(name='Vendors').exists()

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})

@require_POST
def add_to_basket(request, product_id):
    if not request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': 'Требуется авторизация',
                'login_url': f"{reverse('login')}?next={request.META.get('HTTP_REFERER')}"
            }, status=403)
        return redirect(f"{reverse('login')}?next={request.META.get('HTTP_REFERER')}")

    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # Логика добавления в корзину
    basket_item, created = Basket.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        basket_item.quantity += quantity
        basket_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'basket_count': request.user.basket_items.count(),
            'message': f'Товар "{product.name}" добавлен в корзину!'
        })
    
    messages.success(request, f'Товар "{product.name}" добавлен в корзину!')
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def update_basket(request, basket_id):
    basket_item = get_object_or_404(Basket, id=basket_id, user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        basket_item.quantity = quantity
        basket_item.save()
    else:
        basket_item.delete()
    
    return redirect('basket')

@login_required
def remove_from_basket(request, basket_id):
    basket_item = get_object_or_404(Basket, id=basket_id, user=request.user)
    basket_item.delete()
    messages.success(request, 'Товар удален из корзины')
    return redirect('basket')

@login_required
def profile_view(request):
    return render(request, 'registration/profile.html')

@login_required
def delete_product_image(request, pk):
    image = get_object_or_404(ProductImage, pk=pk)
    if request.user.vendor == image.product.vendor:
        image.delete()
    return redirect('add_product_images', pk=image.product.pk)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Vendors').exists())
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, user=request.user)
        if form.is_valid():
            product = form.save()
            product.vendor = request.user.vendor  # Устанавливаем поставщика
            product.save()  # Теперь сохраняем (будет pk)
            form.save_m2m()  # Сохраняем ManyToMany поля
            
            # Основное изображение
            main_image = request.FILES.get('main_image')
            if main_image:
                product.image = main_image
                product.save()
            
            # Дополнительные изображения
            images = request.FILES.getlist('images')[:4]  # Макс. 4 изображения
            for img in images:
                ProductImage.objects.create(product=product, image=img)
                
            return redirect(product.get_absolute_url())
    else:
        product_form = ProductForm(user=request.user)
    
    return render(request, 'products/add_product.html', {
        'product_form': product_form
    })

@login_required
def add_product_images(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        images = request.FILES.getlist('images')[:5]  # Ограничение до 5 изображений
        for img in images:
            ProductImage.objects.create(product=product, image=img)
        return redirect('product_detail', pk=product.pk)
    
    return render(request, 'products/add_product_image.html', {
        'product': product
    })

@login_required
def checkout(request):
    # Получаем товары в корзине с предварительной выборкой связанных продуктов
    basket_items = Basket.objects.filter(user=request.user).select_related('product')
    
    if not basket_items.exists():
        messages.warning(request, "Ваша корзина пуста")
        return redirect('basket')
    
    # Рассчитываем общую сумму
    total = sum(item.total_price() for item in basket_items)
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                # Создаем заказ
                order = Order.objects.create(
                    user=request.user,
                    total_amount=total,
                    shipping_address=form.cleaned_data['address'],
                    phone_number=form.cleaned_data['phone'],
                    notes=form.cleaned_data.get('notes', '')
                )
                
                # Переносим товары из корзины в заказ
                for item in basket_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )
                
                # Очищаем корзину
                basket_items.delete()
                
                messages.success(request, "Ваш заказ успешно оформлен!")
                return redirect('order_detail', order_id=order.id)
                
            except Exception as e:
                messages.error(request, f"Произошла ошибка: {str(e)}")
                # Можно добавить логирование ошибки
                # logger.error(f"Order creation error: {str(e)}")
    else:
        # Предзаполняем форму данными пользователя, если они есть
        initial_data = {}
        if request.user.first_name or request.user.last_name:
            initial_data['name'] = f"{request.user.first_name} {request.user.last_name}".strip()
        if request.user.profile.phone if hasattr(request.user, 'profile') else None:
            initial_data['phone'] = request.user.profile.phone
        
        form = CheckoutForm(initial=initial_data)
    
    return render(request, 'products/checkout.html', {
        'basket_items': basket_items,
        'total': total,
        'form': form
    })
        
@login_required
def basket(request):
    basket_items = Basket.objects.filter(user=request.user).select_related('product')
    
    # Рассчитываем общую сумму
    total = sum(item.total_price() for item in basket_items)
    
    # Добавляем отладочный вывод
    print(f"Корзина пользователя {request.user}: {len(basket_items)} товаров")
    for item in basket_items:
        print(f"- {item.product.name}: {item.quantity} x {item.product.price} = {item.total_price()}")
    print(f"Общая сумма: {total}")
    
    return render(request, 'products/basket.html', {
        'basket_items': basket_items,
        'total': total  # Добавляем общую сумму в контекст
    })


def home(request):
    popular_products = Product.get_popular_products()
    return render(request, 'products/home.html', {
        'popular_products': popular_products
    })

    
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Перенаправляем на страницу входа
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def product_search(request):
    query = request.GET.get('q', '').strip()
    results = Product.objects.none()
    
    if query:
        # Поиск без учета регистра
        results = Product.objects.annotate(
            lower_name=Lower('name'),
            lower_description=Lower('description'),
            lower_category=Lower('main_category__name'),
            lower_subcategory=Lower('subcategory__name')
        ).filter(
            Q(lower_name__icontains=query.lower()) |
            Q(lower_description__icontains=query.lower()) |
            Q(lower_category__icontains=query.lower()) |
            Q(lower_subcategory__icontains=query.lower())
        ).distinct()
    
    return render(request, 'products/search_results.html', {
        'results': results,
        'query': query
    })

def search_autocomplete(request):
    query = request.GET.get('term', '')
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )[:10]
    results = [product.name for product in products]
    return JsonResponse(results, safe=False)

def load_subcategories(request):
    main_category_id = request.GET.get('main_category_id')
    subcategories = SubCategory.objects.filter(main_category_id=main_category_id)
    return render(request, 'products/subcategory_dropdown_list_options.html', {
        'subcategories': subcategories
    })

def category_products(request, category_slug):
    category = get_object_or_404(MainCategory, slug=category_slug)
    subcategories = SubCategory.objects.filter(main_category=category).annotate(
        product_count=Count('products')
    )
    
    # Получаем параметры фильтрации
    selected_subcategories = request.GET.getlist('subcategory')
    selected_sizes = request.GET.getlist('size')
    selected_colors = request.GET.getlist('color')
    
    # Фильтрация товаров
    products = Product.objects.filter(main_category=category)
    
    if selected_subcategories:
        products = products.filter(subcategory_id__in=selected_subcategories)
    
    if selected_sizes:
        products = products.filter(sizes__in=selected_sizes)
    
    if selected_colors:
        products = products.filter(colors__in=selected_colors)
    
    # Получаем уникальные размеры и цвета для фильтров
    sizes = Size.objects.filter(products__in=products).annotate(
        product_count=Count('products')
    ).distinct()
    
    colors = Color.objects.filter(products__in=products).annotate(
        product_count=Count('products')
    ).distinct().order_by('name') 
    
    # Для AJAX запросов
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        products_html = render_to_string('products/product_list_partial.html', {
            'products': products.distinct()
        })
        return JsonResponse({
            'products_html': products_html,
            'products_count': products.count()
        })
    
    return render(request, 'products/category.html', {
        'category': category,
        'products': products.distinct(),
        'subcategories': subcategories,
        'sizes': sizes,
        'colors': colors,
        'selected_subcategories': selected_subcategories,
        'selected_sizes': selected_sizes,
        'selected_colors': selected_colors
    })