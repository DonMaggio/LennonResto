from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy

from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer, BrowsableAPIRenderer

from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from django.views.generic import CreateView
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes

from .serializers import MenuItemSerializer, MenuDetailSerializer, UserCartSerializer, UserOrdersSerializer, UserSerializer
from .models import MenuItem, Cart, Order, OrderItem, Category
from .forms import CustomUserCreationForm

from decimal import Decimal

## View generica
def home(request):
    return render(request, 'home.html')

@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({'message':'Mensaje secreto'})

## View del menu completo
class MenuItemView(generics.ListCreateAPIView):
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

## View del detalle de cada item del menu
class SingleItemView(LoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuDetailSerializer
    login_url = "/login/"
    redirect_field_name = "redirect_to"


    def get_permissions(self): #sobrescribe los permisos predeterminados de la vista
        if self.request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return [IsAdminUser()] ## Solo permite estas acciones a los administradores
        return [AllowAny()] ## Permite a cualquier usuario acceder a los demás métodos (como GET)
    
    def patch(self, request, *args, **kwargs):
        menuitem = MenuItem.objects.get(pk=self.kwargs['pk'])
        menuitem.featured = not menuitem.featured
        menuitem.save()
        return JsonResponse(status=200, data={'message':'Featured status of {} changed to {}'.format(str(menuitem.title) ,str(menuitem.featured))})

## View para visualizar los items del carrito por usuario
class CustomerCartView(LoginRequiredMixin, generics.ListCreateAPIView): #funcionalidad de listar (GET) y crear (POST)
    serializer_class = UserCartSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name='cart.html'
    login_url = "/login/"
    redirect_field_name = "redirect_to"

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

## View de las ordenes que estan creadas para el staff
# GET (listar órdenes) y POST (crear órdenes)
class OrdersView(LoginRequiredMixin, generics.ListCreateAPIView):
    serializer_class = UserOrdersSerializer
    permission_classes = [IsAuthenticated]
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def perform_create(self, serializer): #sobrescribe la lógica predeterminada de cómo se crea un pedido. Se ejecuta con POST.
        cart_items = Cart.objects.filter(user=self.request.user)
        total = self.calculate_total(cart_items)
        order = serializer.save(user=self.request.user, total=total) #Creación de nuevo objeto Order

        for cart_item in cart_items: #Creación de los item en OrderItem por cada item del carrito del usuario
            OrderItem.objects.create(menuitem=cart_item.menuitem, quantity=cart_item.quantity,
                                    unit_price=cart_item.unit_price, price=cart_item.price, order=order)
            cart_item.delete()

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.filter(status=False)
        return Order.objects.filter(user=user, status=False)

    def calculate_total(self, cart_items):
        total = Decimal(0)
        for item in cart_items:
            total += item.price
        return total

## View de una sola orden
class SingleOrderview(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserOrdersSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)


## Vistas para la gestion de usuarios ##
#Lista de todos los usuarios
class UserView(generics.ListCreateAPIView):#
    queryset = User.objects.all()
    serializer_class = UserSerializer
    #permission_classes = [IsAuthenticated]
    #permission_classes = [IsAuthenticatedOrReadOnly]
    #permission_classes = [IsAdminUser]

#Registro de usuarios
class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('menu')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


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
