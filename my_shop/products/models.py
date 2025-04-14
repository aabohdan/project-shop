from django.db import models
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.urls import reverse 



class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.company_name

    def get_absolute_url(self):
        return reverse('vendor_detail', kwargs={'pk': self.pk})
class MainCategory(models.Model):
    MAIN_CATEGORY_CHOICES = [
        ('boys', 'Мальчики'),
        ('girls', 'Девочки'),
        ('baby', 'Малыши'),
        ('shoes', 'Обувь'),
        ('textile', 'Текстиль'),
    ]
    
    name = models.CharField(
        max_length=20,
        choices=MAIN_CATEGORY_CHOICES,
        unique=True,
        verbose_name="Тип категории"
    )
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.get_name_display())
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.get_name_display()
    
    class Meta:
        verbose_name = "Главная категория"
        verbose_name_plural = "Главные категории"

class SubCategory(models.Model):
    main_category = models.ForeignKey(
        MainCategory,
        on_delete=models.CASCADE,
        null=True,  # Временно разрешаем NULL
        blank=True
    )
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(verbose_name="Слаг (URL)")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.main_category.get_name_display()} - {self.name}"
    
    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        unique_together = ('main_category', 'slug')

class Size(models.Model):
    name = models.CharField(max_length=10, verbose_name="Размер")
    description = models.CharField(max_length=50, verbose_name="Описание", null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"

class Color(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    hex_code = models.CharField(max_length=7, verbose_name="HEX-код", null=True, blank=True)
    
    class Meta:
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"
        ordering = ['name']  # Сортировка по умолчанию по имени
        
    def __str__(self):
        return self.name

class Product(models.Model):
    main_category = models.ForeignKey(
        'MainCategory',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Главная категория"
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Подкатегория",
        related_name='products'
    )
    slug = models.SlugField(unique=True, blank=True)
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    composition = models.TextField(verbose_name="Состав")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='products/', verbose_name="Изображение", null=True, blank=True)
    sizes = models.ManyToManyField(Size, verbose_name="Размеры", related_name='products')
    colors = models.ManyToManyField(Color, verbose_name="Цвета", related_name='products')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуемый")
    
    def get_main_category_name(self):
        return self.main_category.get_name_display() if self.main_category else "Без категории"
    
    def get_price_display(self):
        return f"{self.price:.2f} бел.руб."
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name
    
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Поставщик"
    )
    
    def get_absolute_url(self):
        if self.pk is None:
            raise ValueError("Product must be saved before getting absolute URL")
        return reverse('product_detail', kwargs={'pk': self.pk})
    
    views = models.PositiveIntegerField(default=0)
    
    @classmethod
    def get_popular_by_views(cls, limit=8):
        return cls.objects.order_by('-views')[:limit]
    
    @classmethod
    def get_popular_products(cls, limit=8):
        """Возвращает самые популярные товары (по количеству заказов)"""
        return cls.objects.annotate(
            order_count=models.Count('orderitem')
        ).order_by('-order_count', '-created_at')[:limit]
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name', 'slug']),
            models.Index(fields=['is_featured']),
        ]
        
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='additional_images'
    )
    image = models.ImageField(
        upload_to='product_images/',
        verbose_name="Дополнительное изображение"
    )
    
    def __str__(self):
        return f"Изображение для {self.product.name}"
    
    def clean(self):
        if not self.image:
            raise ValidationError("Изображение обязательно")
        
    def save(self, *args, **kwargs):
        self.full_clean()  # Вызовет clean() перед сохранением
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        
class Basket(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='basket_items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    def total_price(self):
        return self.product.price * self.quantity
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    phone_number = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=(
        ('pending', 'В обработке'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен')
    ), default='pending')

    def __str__(self):
        return f"Order #{self.id}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.price * self.quantity
    
class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField('Адрес', blank=True, null=True)  
    birth_date = models.DateField('Дата рождения', blank=True, null=True) 
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    
    def __str__(self):
        return f'Профиль {self.user.username}'

@receiver(post_save, sender=User)
def handle_user_save(sender, instance, created, **kwargs):
    """
    Автоматически создаёт или обновляет профиль
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        # Безопасное обновление профиля
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            Profile.objects.create(user=instance)