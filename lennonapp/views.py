from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy

from django.template.loader import get_template

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer, BrowsableAPIRenderer

from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from django.views.generic import CreateView, View
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes

from .serializers import MenuItemSerializer, MenuDetailSerializer, UserCartSerializer, UserOrdersSerializer, UserSerializer, OrdersSerializer
from .models import MenuItem, Cart, Order, OrderItem, Category
from .forms import CustomUserCreationForm

from decimal import Decimal

from .utils import rendertopdf

## View generica
def home(request):
    return render(request, 'home.html')

## View del menu completo
class MenuItemView(generics.ListAPIView):
    format = None
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name='menu.html'

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request, *args, **kwargs):
        self.object = self.queryset.all()
        categorias = Category.objects.all()
        cart_items_count = 0
        if request.user.is_authenticated:
            cart_items_count = Cart.objects.filter(user=request.user).count()
        return Response({'menu':self.object, 'cat':categorias, 'cart_items_count': cart_items_count})
    
## View para crear items
class CreateMenuItemView(LoginRequiredMixin, generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    serializer_class = MenuDetailSerializer
    queryset = MenuItem.objects.all()
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'add_item_menu.html'
    success_url = reverse_lazy('menu')

    def get(self, request, *args, **kwargs):
        categorias = Category.objects.all()
        return Response({'cat':categorias})
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect(self.success_url)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

## View del detalle de cada item para modificar
class SingleItemView(LoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    queryset = MenuItem.objects.all()
    serializer_class = MenuDetailSerializer
    template_name = 'edit_item_menu.html'
    renderer_classes = [TemplateHTMLRenderer]
    success_url = reverse_lazy('menu')
    
    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        return redirect(self.success_url)

    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        return redirect(self.success_url)


## View para visualizar los items del carrito por usuario
class CustomerCartView(LoginRequiredMixin, generics.ListCreateAPIView): #funcionalidad de listar (GET) y crear (POST)
    permission_classes = [IsAuthenticated]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    serializer_class = UserCartSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name='cart.html'

    def get_queryset(self): #Filtra los objetos del modelo Cart y devuelve solo aquellos que pertenecen al usuario actual (self.request.user).
        cart = Cart.objects.filter(user=self.request.user)
        return cart

    def perform_create(self, serializer):
        menuitem = serializer.validated_data.get('menuitem')
        quantity = serializer.validated_data.get('quantity', 1)
        item = get_object_or_404(MenuItem, id=menuitem.id)
        price = quantity * item.price
        serializer.save(user=self.request.user, price=price)

    def delete(self, request, *args, **kwargs):
        menuitem_id = request.data.get('menuitem')
        if not menuitem_id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'No item id provided'})
        cart_item = Cart.objects.filter(user=request.user, menuitem__id=menuitem_id).first()
        if not cart_item:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Item not found'})
        cart_item.delete()
        queryset = self.get_queryset()
        total_price = sum(item.price for item in queryset)
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response({'cart': serializer.data, 'total_price': total_price}, status=status.HTTP_200_OK)
        return Response({'cart': [], 'total_price': 0}, status=status.HTTP_200_OK)
        
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        total_price = sum(item.price for item in queryset)
        return Response({'cart':serializer.data, 'total_price':total_price})

## View de las ordenes que estan creadas
# POST (crear órdenes)
class OrdersView(LoginRequiredMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    serializer_class = UserOrdersSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name='old_orders.html'

    def perform_create(self, serializer): #sobrescribe la lógica predeterminada de cómo se crea un pedido. Se ejecuta con POST.
        cart_items = Cart.objects.filter(user=self.request.user)
        total = self.calculate_total(cart_items)
        order = serializer.save(user=self.request.user, total=total) #Creación de nuevo objeto Order

        for cart_item in cart_items: #Creación de los item en OrderItem por cada item del carrito del usuario
            OrderItem.objects.create(
                menuitem=cart_item.menuitem, 
                quantity=cart_item.quantity,
                unit_price=cart_item.menuitem.price, 
                price=cart_item.price, 
                order=order)
            cart_item.delete()

        # Enviar correo de confirmación al usuario
        self.send_order_confirmation_email(order)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def calculate_total(self, cart_items):
        total = Decimal(0)
        for item in cart_items:
            total += item.price
        return total
    
    def send_order_confirmation_email(self, order):
        subject = 'Confirmación de pedido Lennon'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_email = self.request.user.email
        if not recipient_email:
            print("No se puede enviar el correo. El usuario no tiene una dirección de correo electrónico válida.")
            return

        template = get_template('email/email_order_success.html')
        content = template.render({
            'order': order, 
            'user': self.request.user,
            'order_items': order.orderitem_set.all()})
        
        #Correo (titulo, cuerpo, emisor, destinatario)
        msg = EmailMultiAlternatives(
            subject,
            f'Hola {self.request.user.username},\n\nTu pedido con ID {order.id} ha sido confirmado.',
            from_email,
            [recipient_email],
        )

        msg.attach_alternative(content, 'text/html')
        msg.send()

#View para listar todas las ordenes por usuario
class OrderListView(LoginRequiredMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    serializer_class = UserOrdersSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name='orders_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all().order_by('-id')
        return Order.objects.filter(user=user).order_by('-id')
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'orders':serializer.data})

## View de una sola orden para cambio de status
class ChangeOrderview(LoginRequiredMixin, generics.UpdateAPIView):
    permission_classes = [IsAdminUser]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    serializer_class = OrdersSerializer
    success_url = reverse_lazy('pending-orders')
    
    def get_queryset(self):
        return Order.objects.all()
    
    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        return redirect(self.success_url)

    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        return redirect(self.success_url)

## View de ordenes prendientes
class PendingOrdersView(LoginRequiredMixin, generics.ListAPIView):
    permission_classes = [IsAdminUser]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    serializer_class = OrdersSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name='pending_orders.html'

    def get_queryset(self):
        return Order.objects.filter(status=False).order_by('-id')
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'orders':serializer.data})

## View de ordenes completadas 
class CompletedOrdersView(LoginRequiredMixin, generics.ListAPIView):
    permission_classes = [IsAdminUser]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    serializer_class = OrdersSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name='completed_orders.html'

    def get_queryset(self):
        return Order.objects.filter(status=True).order_by('-id')
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'orders':serializer.data})


#Registro de usuarios
class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

#Cambio de contraseña
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    permission_classes = [IsAuthenticated]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    form_class = PasswordChangeForm
    template_name = 'registration/password_change.html'
    success_url = reverse_lazy('menu')

"""
## Utilizacion de viewsets ##
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer
    #renderer_classes = [TemplateHTMLRenderer]
    #template_name='old_orders.html'
    
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return [IsAdminUser()]
        return [AllowAny()]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'orders':serializer.data})
"""

#Impresion de Order
class PrintOrder(LoginRequiredMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    serializer_class = OrdersSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        order_id = self.kwargs.get('pk') 
        return Order.objects.filter(id=order_id)
    
    def get(self, request, *args, **kwargs):
        orders = self.get_queryset()
        serializer = self.get_serializer(orders, many=True)
        data = {'orders':serializer.data}
        pdf = rendertopdf('ticket/order_tickets.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
