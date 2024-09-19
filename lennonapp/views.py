from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer, BrowsableAPIRenderer

from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from django.contrib.auth.models import User, Group

from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes

from .serializers import MenuItemSerializer, MenuDetailSerializer, UserCartSerializer, UserOrdersSerializer, UserSerializer
from .models import MenuItem, Cart, Order, OrderItem

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
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    renderer_classes = [TemplateHTMLRenderer]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request, *args, **kwargs):
        self.object = self.queryset.all()
        return Response({'menu':self.object}, template_name='menu.html')

## View del detalle de cada item del menu
class SingleItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuDetailSerializer

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
class CustomerCartView(generics.ListCreateAPIView): #funcionalidad de listar (GET) y crear (POST)
    serializer_class = UserCartSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]

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
        if menuitem_id:
            cart_item = get_object_or_404(Cart, user=request.user, menuitem__id=menuitem_id)
            cart_item.delete()
            return Response(status=status.HTTP_200_OK, data={'message': 'Item removed from cart'})
        else:
            Cart.objects.filter(user=request.user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT, data={'message': 'All items removed from cart'})
        
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        total_price = sum(item.price for item in queryset)
        return Response({'cart':serializer.data, 'total_price':total_price}, template_name='old_cart.html')

## View de las ordenes que estan creadas para el staff
# GET (listar órdenes) y POST (crear órdenes)
class OrdersView(generics.ListCreateAPIView):
    serializer_class = UserOrdersSerializer
    permission_classes = [IsAuthenticated]

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
        if user.groups.filter(name='manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)

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
        if user.groups.filter(name='manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)


## Vistas para la gestion de usuarios ##
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
