from django.db import models

    
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True, verbose_name="Слаг (URL)")
   

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class Size(models.Model):
    name = models.CharField(max_length=10, verbose_name="Размер")
    description = models.CharField(max_length=50, verbose_name="Описание размера", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"

class Color(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название цвета")
    hex_code = models.CharField(max_length=7, verbose_name="HEX-код цвета", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название товара")
    description = models.TextField(verbose_name="Описание товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    categories = models.ManyToManyField(Category, verbose_name="Категории", related_name='products')  
    sizes = models.ManyToManyField(Size, verbose_name="Размеры", related_name='products')
    colors = models.ManyToManyField(Color, verbose_name="Цвета", related_name='products')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

class ProductImage(models.Model):
    image = models.ImageField(upload_to='products/media_goods/', verbose_name="Изображение товара")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Товар")

    def __str__(self):
        return f"Изображение для {self.product.name}"

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар", related_name='reviews')
    author_name = models.CharField(max_length=100, verbose_name="Имя автора")
    text = models.TextField(verbose_name="Текст отзыва")
    rating = models.PositiveIntegerField(verbose_name="Рейтинг", default=5, choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Отзыв от {self.author_name} на {self.product.name}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"