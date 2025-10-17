from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Avg, IntegerField, FloatField, F
from django.db.models.functions import Cast



class Category(models.Model):
    title = models.CharField(max_length=150, verbose_name="Наименование категории")
    image = models.ImageField(upload_to='categories/', null=True, blank=True, 
                              verbose_name="Изображения")
    slug = models.SlugField(unique=True, null=True) # Слаг для красивого url
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name="Категория", related_name='subcaregories') # Связываем модель саму с собой, выстраивая иерархию - категория, подкатегория


    def get_absolute_url(self):
        '''Ссылка на стрнаицу категории'''
        return reverse('category_detail', kwargs={'slug': self.slug})
    
    
    # для красивого отображения (пользователи, админка, шаблоны)
    def __str__(self):   
        return self.title 
    
    
     # для точного представления объекта (разработчики, отладка)
    def __repr__(self): 
        return f'Категория: pk={self.pk}, title={self.title}'
    
    
    def get_parent_category_photo(self):
        '''Для получения картинки родительской категории'''
        if self.image:
            return self.image.url
        
        
        
    # Делаем админку с русскими словами 
    class Meta: 
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="Наименование товара")
    price = models.FloatField(verbose_name='Цена')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания')
    watched =models.IntegerField(default=0, verbose_name='просмотры')
    quantity = models.IntegerField(default=0, verbose_name='Количество на складе')
    description = models.TextField(default='Здесь скоро будет описание', 
                                   verbose_name='Описание товара')
    info = models.TextField(default='Дополнительная информация о товаре', 
                            verbose_name='Информация о товаре')
    category =models.ForeignKey(Category, on_delete=models.CASCADE, 
                                verbose_name='Категория', related_name='products')
    slug = models.SlugField(unique=True, null=True)
    size = models.IntegerField(default=30, verbose_name='Размер в мм')
    color = models.CharField(max_length=30, default='Серебро', verbose_name='Цвет/Материал')    
    
    def get_absolute_url(self):
        return reverse('product_page', kwargs={'slug':self.slug}) # Связывание модель с маршрутом урл
    
    def __str__(self):   
        return self.title 
    
    def __repr__(self): 
        return f'Товар: pk={self.pk}, title={self.title}, price={self.price}'
    
    
    def get_first_photo(self):
        if self.images.first():
            return self.images.first().image.url
        else:
            return 'https://www.yandex.ru/images/search?img_url=https%3A%2F%2Fstatic.tildacdn.com%2Ftild3137-3430-4432-b239-333364643064%2Fno_image-1100x600.png&lr=11469&pos=34&rpt=simage&source=serp&stype=image&text=%D1%84%D0%BE%D1%82%D0%BE%20%D0%BD%D0%B5%20%D0%BD%D0%B0%D0%B9%D0%B4%D0%B5%D0%BD%D0%BE'
    
    
    class Meta: 
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        
        
class Gallery(models.Model):
    image = models.ImageField(upload_to='products/', verbose_name='Изображение') # В будущем картинки будут храниться в папке Медиа/продуктс
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')  # Связываем картинку с продуктом
    
    
    class Meta: 
        verbose_name = 'Изображение'
        verbose_name_plural = 'Галерея товаров'


CHOICES = (
    ('5', 'Отлично'),
    ('4', 'Хорошо'),
    ('3', 'Нормально'),
    ('2', 'Ну такое'),
    ('1', 'Плохо')
)


class Review(models.Model):
    '''Модель отзывов'''
    text = models.TextField(verbose_name='Ваш отзыв')
    grade = models.CharField(max_length=20, choices=CHOICES, blank=True, null=True, 
                             verbose_name='Оценка')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт отзыва')   
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата') 
    
    @classmethod
    def get_average_rating(cls, product):
        '''Оптимизированный метод с агрегацией в БД'''
        return cls.objects.filter(
            product=product,
            grade__isnull=False
        ).annotate(
            numeric_grade=Cast('grade', IntegerField())
        ).aggregate(
            avg_rating=Avg('numeric_grade', output_field=FloatField())
        )['avg_rating'] or 0
    
    @classmethod
    def get_rounded_average(cls, product):
        '''Возвращает округленный средний рейтинг'''
        avg = cls.get_average_rating(product)
        return round(avg) if avg else 0
        
        
    def __str__(self):
        '''В админке возвращаем имя пользователя'''
        return self.author.username 
    
    class Meta:
        verbose_name='Отзыв'
        verbose_name_plural = 'Отзывы'  
     

class FavoriteProduct(models.Model):
    '''Избранные товары'''
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')

    def __str__(self):
        return self.product.title
    
    
    class Meta:
        verbose_name='Избранный товар'
        verbose_name_plural = 'Избранный товары' 
        
        
class Mail(models.Model):
    '''Почтовая рассылка'''
    # Почта уникальная, чтобы не было дублированности рассылок
    mail = models.EmailField(unique=True, verbose_name='Почта')
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                             blank=True, null=True)
    
    class Meta:
        verbose_name='Почта'
        verbose_name_plural = 'Почты'
        

class Customer(models.Model):
    '''Контактная информация заказчика'''
    user = models.OneToOneField(User, models.SET_NULL, blank=True, 
                                null=True, verbose_name='Пользователь')
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    email = models.EmailField(max_length=255, verbose_name='Почта')
    phone = models.CharField(max_length=255, null=True, blank=True, verbose_name='Контактный номер')
    
    def __str__(self):
        return self.first_name
    
    class Meta:
        verbose_name='Покупатель'
        verbose_name_plural = 'Покупатели'


class Order(models.Model):
    '''Корзинка'''
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL,blank=True, 
                                null=True, verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    is_completed = models.BooleanField(default=False, verbose_name='Завершен')
    shipping = models.BooleanField(default=True, verbose_name='Доставка')
    
    def __str__(self):
        return str(self.pk)
    
    class Meta:
        verbose_name='Заказ'
        verbose_name_plural = 'Заказы'
        
    @property
    def get_cart_total_price(self):
        '''Сумма товаров корзинки'''
        order_products = self.ordered.all()
        total_price = sum([product.get_total_price for product in order_products])
        return total_price
    
    
    @property
    def get_cart_total_quantity(self):
        '''Получения кол-во товаров корзины'''
        order_products = self.ordered.all()
        total_quantity = sum([product.quantity for product in order_products])
        return total_quantity
    
    @property
    def delivery_cost(self):
        '''Считаем доставку'''
        if self.get_cart_total_price > 2000:
            return 0
        
        total_delivery = 0
        for item in self.ordered.all():
            if item.product.price > 550:
                total_delivery += 50 * item.quantity
            else:
                total_delivery += 5 * item.quantity
        return total_delivery

    @property
    def total_to_pay(self):
        '''Общая сумма к оплате (товары + доставка)'''
        return self.get_cart_total_price + self.delivery_cost
            

class OrderProduct(models.Model):
    '''Привязка определенного товара к корзинке'''
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name='ordered')
    quantity = models.IntegerField(default=0, null=True, blank=True) # Кол-во товара
    added_at = models.DateTimeField(auto_now_add=True) # Дата добавление продукта в корзинкку
    
    class Meta:
        verbose_name='Товар в заказе'
        verbose_name_plural = 'Товары в заказах'
        
    @property
    def get_total_price(self):
        '''Общая сумма одного товара'''
        total_price = self.product.price * self.quantity
        return total_price


class ShippingAdress(models.Model):
    '''Адрес доставки'''
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL,blank=True, 
                                null=True, verbose_name='Пользователь')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    city = models.CharField(max_length=255, verbose_name='Город')
    state = models.CharField(max_length=255, verbose_name='Район')
    street = models.CharField(max_length=255, verbose_name='Улица')
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата создания')
    
    def __str__(self):
        return self.street
    
    class Meta:
        verbose_name='Адрес доставки'
        verbose_name_plural = 'Адреса доставки'
