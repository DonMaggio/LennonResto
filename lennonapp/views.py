from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy

from django.template.loader import get_template

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer, BrowsableAPIRenderer

from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from django.views.generic import CreateView
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

## View generica
def home(request):
    return render(request, 'home.html')

"""
@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({'message':'Mensaje secreto'})
"""

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
        return Response({'menu':self.object, 'cat':categorias})
    
#View para crear items
class CreateMenuItemView(LoginRequiredMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    serializer_class = MenuDetailSerializer
    queryset = MenuItem.objects.all()
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'add_item_menu.html'
    success_url = reverse_lazy('menu')

    def get_permissions(self):
        if self.request.method in [ 'GET', 'PUT', 'PATCH', 'DELETE', 'POST']:
            return [IsAdminUser()]
        return [AllowAny()]

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
    permission_classes = [IsAuthenticated]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    queryset = MenuItem.objects.all()
    serializer_class = MenuDetailSerializer
    template_name = 'edit_item_menu.html'
    renderer_classes = [TemplateHTMLRenderer]
    success_url = reverse_lazy('menu')

    def get_permissions(self):
        if self.request.method in [ 'GET', 'PUT', 'PATCH', 'DELETE', 'POST']:
            return [IsAdminUser()]
        return [AllowAny()]
    
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
# GET (listar órdenes) y POST (crear órdenes)
class OrdersView(LoginRequiredMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    serializer_class = UserOrdersSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name='orders.html'

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

## View de una sola orden
class ChangeOrderview(LoginRequiredMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    serializer_class = OrdersSerializer
    success_url = reverse_lazy('pending-orders')
    
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        return redirect(self.success_url)

    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        return redirect(self.success_url)


## View de ordenes prendientes
class PendingOrdersView(LoginRequiredMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    serializer_class = OrdersSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name='pending_orders.html'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.filter(status=False)
        return Order.objects.filter(user=user, status=False)
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'orders':serializer.data})

## View de ordenes completadas 
class CompletedOrdersView(LoginRequiredMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    login_url = "menu"
    redirect_field_name = "redirect_to"
    serializer_class = OrdersSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name='completed_orders.html'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.filter(status=True)
        return Order.objects.filter(user=user, status=True)
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'orders':serializer.data})


"""
## Vistas para la gestion de usuarios ##
#Lista de todos los usuarios
class UserView(generics.ListCreateAPIView):#
    queryset = User.objects.all()
    serializer_class = UserSerializer
    #permission_classes = [IsAuthenticated]
    #permission_classes = [IsAuthenticatedOrReadOnly]
    #permission_classes = [IsAdminUser]
"""
    
#Registro de usuarios
class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('menu')
    
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
class ManagerUsersView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # Get the 'manager' group
        manager_group = Group.objects.get(name='Manager')
        # Get the users in the 'manager' group
        queryset = User.objects.filter(groups=manager_group)
        return queryset

    def perform_create(self, serializer):
        # Assign the user to the 'manager' group
        manager_group = Group.objects.get(name='Manager')
        user = serializer.save()
        user.groups.add(manager_group)

class ManagerSingleUserView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # Get the 'manager' group
        manager_group = Group.objects.get(name='Manager')
        # Get the users in the 'manager' group
        queryset = User.objects.filter(groups=manager_group)
        return queryset

class DeliveryUserView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        delivery_group = Group.objects.get(name='Delivery')
        queryset = User.objects.filter(groups=delivery_group)
        return queryset

    def perform_create(self, serializer):
        delivery_group = Group.objects.get(name='Delivery')
        user = serializer.save()
        user.groups.add(delivery_group)

class DeliveryUserSingleView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        delivery_group = Group.objects.get(name='Delivery')
        queryset = User.objects.filter(groups=delivery_group)
        return queryset
"""

## Utilizacion de viewsets ##
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = MenuDetailSerializer
    model = MenuItem

    def get_object(self):
        return get_object_or_404(self.model, id=self.kwargs.get('pk'))
    
    def get_queryset(self, pk=None):
        return self.model.objects.all()
    
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return [IsAdminUser()]
        return [AllowAny()]