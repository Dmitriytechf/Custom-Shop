from django.urls import path
from .views import *
from django.views.generic import TemplateView



urlpatterns= [
    path('', Index.as_view(), name='index'),
    path('category/<slug:slug>', SubCategories.as_view(), name='category_detail'),
    path('product/<slug:slug>', ProductPage.as_view(), name='product_page'),
    path('login_registrarion', login_registrarion, name='login_registration'),
    path('login', user_login, name='user_login'),
    path('logout', user_logout, name='user_logout'),
    path('register', registration, name='registration'),
    path('save_review/<int:product_pk>', save_review, name='save_review'),
    path('add_favorite/<slug:product_slug>', save_favotite_product, name='add_favorite'),
    path('product_favorite/', FavoriteProductView.as_view(), name='favorite_product_page'),
    path('save_email', save_subscraibers, name='save_subscraibers'),
    path('cart', cart, name='cart'),
    path('to_car/<int:product_id>/<str:action>', add_to_cart, name='add_to_cart'),
    path('checkout/', checkout, name='checkout')
]



