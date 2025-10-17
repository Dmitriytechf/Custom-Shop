from .models import Product, OrderProduct, Order, Customer


class CartForAuthenticatedUser:
    '''Логика корзины'''
    def __init__(self, request, product_id=None, action=None):
        self.user = request.user
        if product_id and action:
            self.add_or_delete(product_id, action)
    
    
    def get_cart_info(self):
        '''Получение информации о корзинке(кол-во товаров и сумма) и заказчике'''
        customer, created = Customer.objects.get_or_create(user=self.user)
        order, created = Order.objects.get_or_create(customer=customer)
        order_products = order.ordered.all()
        cart_total_quantity = order.get_cart_total_quantity
        cart_total_price = order.get_cart_total_price
        
        return {'order': order, # ID корзинки
                'order_products': order_products, # Все товары в виде QuerySet.
                'cart_total_quantity': cart_total_quantity, # Кол-во товаров
                'cart_total_price': cart_total_price # Сумма товаров
                }
            
    
    def add_or_delete(self, product_id, action):
        '''Добавление и удаление товара по нажатию'''
        order = self.get_cart_info()['order']
        product = Product.objects.get(pk=product_id)
        order_products, created = OrderProduct.objects.get_or_create(order=order, product=product)
        
        if action == 'add' and product.quantity > 0:
            order_products.quantity += 1
            product.quantity -= 1
        elif action == 'delete': 
            order_products.quantity -= 1
            product.quantity += 1
        elif action == 'remove':
            product.quantity += order_products.quantity
            order_products.quantity -= product.quantity
        
        product.save()
        order_products.save()
        
        if order_products.quantity < 1:
            order_products.delete()
                        
    
def get_cart_data(request):
    '''Вывод товаров с корзинки на страничку'''
    cart = CartForAuthenticatedUser(request)
    cart_info = cart.get_cart_info()
    
    return {
            'order': cart_info['order'],
            'order_products': cart_info['order_products'],
            'cart_total_quantity': cart_info['cart_total_quantity'],
            'cart_total_price': cart_info['cart_total_price']
            }
