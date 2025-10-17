from django.contrib import admin
from .models import Product, Category, Gallery, Review, Mail, \
        Customer, Order, OrderProduct, ShippingAdress
from django.utils.safestring import mark_safe



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    '''
    Регистрируем модель Category в админке. 
    Задаём поля, которые будут отображаться в списке всех категорий, 
    и автоматически заполняем slug.
    '''
    
    list_display = ('title', 'parent', 'get_product_count')
    prepopulated_fields = {'slug': ('title',)}
    
    
    @admin.display(description='Количество товаров')
    def get_product_count(self, obj):
        """
        Возвращает количество товаров в категории.
        """
        return obj.products.count()  
    
    
    

class GalleryInline(admin.TabularInline):
    '''
    Класс для того, чтобы можно было добавлять картинки при заполнении модели Product.
    Связываем его с модулью Gallery, откуда и будем брать изображения.
    '''
    fk_name = 'product'
    model = Gallery
    extra = 1 # минимум одна картинка
   
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    '''
    Регистрируем модель Product в админке, указвыая все нужные категории для настройки.
    В inlines добавляем и связываем модели прямо на страницу товара.
    '''
    list_display = ('pk', 'title', 'category', 'quantity','price','size','color','created_at', 'get_photo')
    list_editable = ('quantity','price','size','color') # Эти поля можно редактировать
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('title', 'price')
    list_display_links = ('pk', 'title')
    inlines = (GalleryInline,)
    # Потом добавить readonly_fields для просмотров watched
    
    @admin.display(description='Изображение')
    def get_photo(self, obj):
        if obj.images:
            return mark_safe(f'<img src="{obj.images.all()[0].image.url}" width="100"> ')
        else:
            return '-'
            
    
admin.site.register(Gallery)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'created_at', 'text')
    readonly_fields = ('author', 'text', 'created_at') # Админ не может добавлять эти поля
    
    
    
@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):  
    '''Почтовые подписки''' 
    list_display = ('pk', 'mail', 'user')
    readonly_fields = ('mail', 'user')
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):  
    '''Корзинка'''
    list_display = ('customer', 'created_at', 'is_completed', 'shipping')
    list_filter = ('customer', 'is_completed', 'created_at')

    
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    '''Заказчики'''
    list_display = ('user', 'first_name', 'last_name', 'email')
    readonly_fields = ('user', 'first_name', 'last_name', 'email', 'phone')
    list_filter = ('user',)
    

@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    '''Товары в заказах'''
    list_display = ('product', 'order', 'quantity', 'added_at')
    readonly_fields = ('product', 'order', 'quantity', 'added_at')
    list_filter = ('product',)


@admin.register(ShippingAdress)
class ShippingAdressAdmin(admin.ModelAdmin):
    '''Адрес доставки'''
    list_display = ('customer', 'city', 'state')
    readonly_fields = ('customer', 'city', 'state', 'order', 'street', 'created_at')
    list_filter = ('customer',)
