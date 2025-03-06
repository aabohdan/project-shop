from django.contrib import admin
from .models import Category, ProductImage, Size, Color, Product, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'display_categories')  # Отображаем название, цену и категории
    list_filter = ('categories',)  # Фильтруем по категориям

    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    display_categories.short_description = 'Категории'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'product')
    search_fields = ('author_name', 'product__name')

admin.site.register(ProductImage)