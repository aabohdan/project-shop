from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import CustomLoginView, add_product, add_product_images, delete_product_image, profile, profile_edit
from django.contrib.auth.decorators import user_passes_test

def is_vendor(user):
    return user.groups.filter(name='Vendors').exists()


urlpatterns = [
    path('', views.home, name='home'),
    path('category/<slug:category_slug>/', views.category_products, name='category'),
    path('baby/', views.category_products, {'category_slug': 'baby'}, name='baby'),
    path('girls/', views.category_products, {'category_slug': 'girls'}, name='girls'),
    path('boys/', views.category_products, {'category_slug': 'boys'}, name='boys'),
    path('shoes/', views.category_products, {'category_slug': 'shoes'}, name='shoes'),
    path('textile/', views.category_products, {'category_slug': 'textile'}, name='accessories'),
    path('delivery-payment/', views.delivery_payment, name='delpay'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('search/', views.product_search, name='search'),
    path('search/autocomplete/', views.search_autocomplete, name='search_autocomplete'),
    path('ajax/load-subcategories/', views.load_subcategories, name='load_subcategories'),
    path('add-product/', user_passes_test(lambda u: u.groups.filter(name='Vendors').exists())(views.add_product)),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add-product/', add_product, name='add_product'),
    path('product/<int:pk>/add-images/', views.add_product_images, name='add_product_images'),
    path('product/image/<int:pk>/delete/', views.delete_product_image, name='delete_product_image'),
    path('basket/', views.basket, name='basket'),
    path('basket/add/<int:product_id>/', views.add_to_basket, name='add_to_basket'),
    path('basket/update/<int:basket_id>/', views.update_basket, name='update_basket'),
    path('basket/remove/<int:basket_id>/', views.remove_from_basket, name='remove_from_basket'),
    path('checkout/', views.checkout, name='checkout'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    path('login/', CustomLoginView.as_view(), name='login'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)