from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework import generics

from rest_framework import viewsets

from .serializers import MenuItemSerializer, MenuDetailSerializer, UserCartSerializer, UserOrdersSerializer
from .models import MenuItem, Cart, Order, OrderItem

from decimal import Decimal

# Create your views here.
def home(request):
    return render(request, 'home.html')

class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

##Funcionalidad para obtener (GET), actualizar (PUT o PATCH) y eliminar (DELETE) un único objeto
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


class CustomerCartView(generics.ListCreateAPIView): #funcionalidad de listar (GET) y crear (POST)
    serializer_class = UserCartSerializer

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


class OrdersView(generics.ListCreateAPIView):
    serializer_class = UserOrdersSerializer
    def perform_create(self, serializer): #sobrescribe la lógica predeterminada de cómo se crea un pedido
        cart_items = Cart.objects.filter(user=self.request.user)
        total = self.calculate_total(cart_items)
        order = serializer.save(user=self.request.user, total=total)
        for cart_item in cart_items:
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
    
class SingleOrderview(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserOrdersSerializer
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)
    

#Utilizacion de viewsets
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = MenuDetailSerializer
    queryset = MenuItem.objects.all()
