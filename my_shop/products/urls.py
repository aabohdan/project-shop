from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.home, name='home'),
    path('baby', views.baby, name='baby'),
    path('boys', views.boys, name='boys'),
    path('girls', views.girls, name='girls'),
    path('shoes', views.shoes, name='shoes'),
    path('accessories', views.accessories, name='accessories'),
    path('delivery_and_pay', views.delpay, name='delpay'),
    path('basket', views.basket, name='basket'),
    path('home', views.home, name='home')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)