from django.contrib import admin
from .models import MainCategory, SubCategory, Size, Color, Product, ProductImage

@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ('get_name_display', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'main_category')
    list_filter = ('main_category',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code')

class ProductImageInline(admin.TabularInline):  
    model = ProductImage
    extra = 6
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'main_category', 'subcategory', 'is_featured', 'vendor')
    list_filter = ('main_category', 'subcategory', 'is_featured')
    filter_horizontal = ('sizes', 'colors')
    readonly_fields = ['get_absolute_url'] 
    inlines = [ProductImageInline]


