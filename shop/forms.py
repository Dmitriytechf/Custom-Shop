from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from captcha.fields import CaptchaField

from .models import *


class LoginForm(AuthenticationForm):
    '''Форма аутентификации'''
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',
                                                             'placeholder':'Имя Пользователя'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control',
                                                             'placeholder':'Пароль'}))


class RegistrationForm(UserCreationForm):
    '''Форма регистрации'''
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                           'placeholder': 'Имя Пользователя'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control',
                                                         'placeholder': 'Почта'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                               'placeholder': 'Пароль'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                               'placeholder': 'Подтвердите пароль'}))
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ('username', 'email')
        
        
class ReviewForm(forms.ModelForm):
    '''Форма для отзывов'''
    
    class Meta:
        model = Review
        fields = ('text', 'grade') # Показываем эти поля
        widgets = {'text': forms.Textarea(attrs={'class': 'form-control', 
                                                 'placeholder': 'Пишите здесь...'}),
                   'grade': forms.Select(attrs={'class': 'form-control', 
                                                 'placeholder': 'Ваша оценка'})}
        

class CustomerForm(forms.ModelForm):
    '''Контактная информация'''        
    
    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'phone', 'email')
        widgets = {'first_name': forms.TextInput(attrs={'class': 'form-control', 
                                                 'placeholder': 'Пишите здесь имя...'}),
                   'last_name': forms.TextInput(attrs={'class': 'form-control', 
                                                 'placeholder': 'Пишите здесь фамилию...'}),
                   'email': forms.EmailInput(attrs={'class': 'form-control',
                                                    'placeholder': 'Пишите здесь почту...'}),
                   'phone': forms.TextInput(attrs={'class': 'form-control', 
                                                 'placeholder': 'Пишите здесь номер...'})}
        

class ShippingAdressForm(forms.ModelForm):
    '''Адрес доставки'''
    
    class Meta:
        model = ShippingAdress
        fields = ('city', 'state', 'street')
        widgets = {'city': forms.TextInput(attrs={'class': 'form-control', 
                                                 'placeholder': 'Напишите город'}),
                   'state': forms.TextInput(attrs={'class': 'form-control', 
                                                 'placeholder': 'Напишите район'}),
                   'street': forms.TextInput(attrs={'class': 'form-control', 
                                                 'placeholder': 'Напишите улицу'})}
