from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from random import randint
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.utils import IntegrityError

from .models import Category, Product, Review, FavoriteProduct, Mail
from .forms import LoginForm, RegistrationForm, ReviewForm, ShippingAdressForm, CustomerForm
from .utils import CartForAuthenticatedUser, get_cart_data


class Index(ListView):
    '''Главная страница'''
    model = Product
    context_object_name = 'categories'
    extra_context = {'title': 'Главная страница'}
    template_name = 'shop/index.html'

    def get_queryset(self):
        '''Вывод родительских категорий'''
        categories = Category.objects.filter(parent=None) # Только родительские категории
        return categories
    
    
    def get_context_data(self, **kwargs):
        '''Вывод на страничку доп. элементов'''
        context = super().get_context_data(**kwargs)
        # Вывод популярных товаров (threding_products)
        context["top_products"] = Product.objects.order_by('-watched')[:9]
        
        return context
    
    
    
class SubCategories(ListView):
    '''Вывод подкатегории на отдельной страничке'''
    model = Product
    context_object_name = 'products'
    template_name = 'shop/category_page.html'
    
    def get_queryset(self):
        '''Получение товаров подкатегории'''
        type_filds = self.request.GET.get('type')
        if type_filds:
            products = Product.objects.filter(category__slug=type_filds)
            return products
            
        parent_category = Category.objects.get(slug=self.kwargs['slug']) 
        subcaregories = parent_category.subcaregories.all()
        products = Product.objects.filter(category__in=subcaregories).order_by('?')
        
        sort_filds = self.request.GET.get('sort')
        if sort_filds:
            products = products.order_by(sort_filds)
            return products
        
        return products

    def get_context_data(self, **kwargs):
        '''Добавляем категории в контекст'''
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent=None)
        parent_category = Category.objects.get(slug=self.kwargs['slug'])
        context['category'] = parent_category
        context['title'] = parent_category.title
        return context



class ProductPage(DetailView):
    '''Вывод товара на отдельной странице'''
    model = Product
    context_object_name = 'product'
    template_name = 'shop/product_page.html'
    
    def get_context_data(self, **kwargs):
        '''Вывод на страничку дополнительных элементов'''
        # Получаем базовый контекст от родительского класса
        context = super().get_context_data(**kwargs)
        
        # Получаем продукт по slug из URL
        product = Product.objects.get(slug=self.kwargs['slug'])
        context['title'] = product
        
        # products = Product.objects.filter(category=product.category)
        # data = []
        # for i in range(5):
        #     random_index = randint(0, len(products) - 1)
        #     random_product = products[random_index]
        #     if random_product not in data and str(random_product) != product.title:
        #         data.append(random_product)
        
        # Исключаем(exclude) из рекомендуемых наш товар и фильтруем по категории
        data = Product.objects.all().exclude(slug=self.kwargs['slug']).filter(category=product.category)
        context['products'] = data 
        
        # Достаем отзыв продукта и сортируем убыванию
        context['reviews'] = Review.objects.filter(product=product).order_by('-pk') 
        
        context['reviews_count'] = Review.objects.filter(product=product).count()
        # Вычисляем средний рейтинг
        avg_rating = Review.get_rounded_average(product)
        context['avg_rating'] = avg_rating
        
        # Если пользователь прошел аутентификацию, то он может оставлять отзывы
        if self.request.user.is_authenticated:
            context['review_form'] = ReviewForm
            
        return context
    
    
def login_registrarion(request):
    context = {'title': 'Войти или зарегестрироваться',
               'login_form': LoginForm,
               'registration_form': RegistrationForm}
    
    return render(request, 'shop/login_registration.html', context)


def user_login(request):
    form = LoginForm(data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('index')
    else:
        messages.error(request, 'Не верное имя пользователя или пароль')
        return redirect('login_registration')
        

def user_logout(request):
    logout(request)
    return redirect('index')


def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Сохраняем и получаем пользователя
            login(request, user)  # Авторизуем пользователя
            messages.success(request, 'Аккаунт успешно зарегистрирован и вы вошли в систему')
            return redirect('login_registration')  # Перенаправляем на главную
        else:
            messages.error(request, 'Ошибка регистрации')
            return redirect('login_registration')
    else:
        form = RegistrationForm()
    return render(request, 'login_registration.html', {'form': form})


def save_review(request, product_pk):
    '''Слхранение отзыва'''
    form = ReviewForm(data=request.POST) # Достаем данные с пост запроса
    if form.is_valid():
        product = get_object_or_404(Product, pk=product_pk)
        review = form.save(commit=False)
        review.author = request.user
        review.product = product
        review.save()        
        return redirect('product_page', product.slug)
    
    # Если что-то пошло не так, перенаправляем обратно на страницу товара
    product = get_object_or_404(Product, pk=product_pk)
    return redirect('product_page', product.slug)


def save_favotite_product(request, product_slug):
    '''Операции с избранными товарами'''
    if request.user.is_authenticated:
        user = request.user
        product = Product.objects.get(slug=product_slug) # продукт по слагу
        favorite_products = FavoriteProduct.objects.filter(user=user)
        
        # Более эффективный способ обрадобтик запросов БД, чем до этого
        if FavoriteProduct.objects.filter(user=user, product=product).exists():
            FavoriteProduct.objects.filter(user=user, product=product).delete()
        else:
            FavoriteProduct.objects.create(user=user, product=product)
        
        # Чтобы остаться на той же странице
        next_page = request.META.get('HTTP_REFERER', 'category_detail')
        return redirect(next_page)


class FavoriteProductView(LoginRequiredMixin, ListView):
    '''Вывод избранных товаров'''
    model = FavoriteProduct
    context_object_name = 'products'
    template_name = 'shop/favorite_products.html'
    
    login_url = 'registration' # URL для перенаправления неавторизованных пользователей
    
    def get_queryset(self):
        '''Получаем избранные товары конкретного пользователя'''
        user = self.request.user # получаем пользователя
        favs = FavoriteProduct.objects.filter(user=user)
        products = [i.product for i in favs]
        return products
    

def save_subscraibers(request):
    '''Собиратель почтовых адресов'''
    email = request.POST.get('email') # отлавливаем мэйл с формы
    user = request.user if request.user.is_authenticated else None
    if email:
        try:
            Mail.objects.create(mail=email, user=user)
            messages.success(request, 'Email успешно сохранен')
        except IntegrityError:
            messages.error(request, 'Вы уже вводили данный email')
    return redirect('index') 


def cart(request):
    '''Страница корзины'''
    if not request.user.is_authenticated:
        return redirect('login_registration')
    cart_info = get_cart_data(request)
    context = {'order': cart_info['order'],
            'order_products': cart_info['order_products'],
            'cart_total_quantity': cart_info['cart_total_quantity'],
            'cart_total_price': cart_info['cart_total_price'],
            'total_to_pay': cart_info['order'].total_to_pay,
            'delivery_cost': cart_info['order'].delivery_cost}
    
    return render(request, 'shop/cart.html', context)


def add_to_cart(request, product_id, action):
    '''Страница корзины'''
    if request.user.is_authenticated:
        CartForAuthenticatedUser(request, product_id, action)
        return redirect('cart')
    else:
        messages.error('Стойте! Вам нужно зарегистрироваться')
        return redirect('login_registration')
    
    
def checkout(request):
    '''Страница оформления заказа'''
    if not request.user.is_authenticated:
        return redirect('login_registration')
    
    cart_info = get_cart_data(request)
    
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        shipping_form = ShippingAdressForm(request.POST)
        
        if customer_form.is_valid() and shipping_form.is_valid():
            # Сохраняем данные
            customer = customer_form.save()
            shipping = shipping_form.save(commit=False)
            shipping.customer = customer
            shipping.save()
            
            # Обновляем заказ
            order = cart_info['order']
            order.customer = customer
            order.is_completed = True
            order.save()
            
            messages.success(request, 'Покупка прошла успешно')
            return redirect('cart')  
    else:
        customer_form = CustomerForm()
        shipping_form = ShippingAdressForm()

    context = {'order': cart_info['order'],
            'order_products': cart_info['order_products'],
            'cart_total_quantity': cart_info['cart_total_quantity'],
            'cart_total_price': cart_info['cart_total_price'],
            'customer_form': CustomerForm(),
            'shipping_form': ShippingAdressForm(),
            'delivery_cost': cart_info['order'].delivery_cost,
            'total_to_pay': cart_info['order'].total_to_pay,
            'title': 'Оформление заказа'}
    return render(request, 'shop/checkout.html', context)
