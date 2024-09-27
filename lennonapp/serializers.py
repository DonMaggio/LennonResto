from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, User, OrderItem
from decimal import Decimal
from datetime import datetime

class CategorySerializer(serializers.ModelSerializer): #serializador para relacionar la clase Category
    class Meta:
        model = Category
        fields = ['title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    image = serializers.ImageField(required=True)
    description = serializers.CharField(required=True)
    price = serializers.DecimalField(decimal_places=0, max_digits=6)
    #category = serializers.StringRelatedField() => me muestra lo definido en __str__ del model Category que es su ForeingKey
    
    class Meta:
        model = MenuItem
        fields = ('id', 'title', 'price', 'image', 'description', 'category')

class MenuDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    image = serializers.ImageField(required=True)
    description = serializers.CharField(required=True)
    #category = serializers.StringRelatedField()
    #category = CategorySerializer(read_only=False)
    #category = CategorySerializer()
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)
    
    class Meta:
        model = MenuItem
        fields = ('id', 'title', 'price', 'description', 'image', 'category')

class UserCartSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=0, source='menuitem.price', read_only=True )
    name = serializers.CharField(source='menuitem.title', read_only=True)

    class Meta:
        model = Cart
        fields = ['user_id', 'menuitem', 'name', 'quantity', 'unit_price', 'price']
        extra_kwargs = {
            'price': {'read_only': True}
        }

class UserOrdersSerializer(serializers.ModelSerializer):
    Date = serializers.SerializerMethodField()
    date = serializers.DateTimeField(write_only=True, default=datetime.now)
    order_items = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'Date', 'order_items']
        extra_kwargs = {
            'total': {'read_only': True}
        }

    def get_Date(self, obj):
        return obj.date.strftime('%Y-%m-%d')
    
    def get_order_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        serializer = OrderItemSerializer(order_items, many=True, context={'request': self.context['request']})
        return serializer.data

class OrderItemSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=0, source='menuitem.price', read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=0, read_only=True)
    name = serializers.CharField(source='menuitem.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['name', 'quantity', 'unit_price', 'price']
        extra_kwargs = {
            'menuitem': {'read_only': True}
        }

class OrdersSerializer(serializers.ModelSerializer):
    Date = serializers.SerializerMethodField()
    date = serializers.DateTimeField(write_only=True, default=datetime.now)
    order_items = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'Date', 'order_items']
        extra_kwargs = {
            'total': {'read_only': True}
        }

    def get_Date(self, obj):
        return obj.date.strftime('%Y-%m-%d')
    
    def get_order_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        serializer = OrderItemSerializer(order_items, many=True, context={'request': self.context['request']})
        return serializer.data

    def get_user(self, obj):
        return obj.user.get_full_name() if obj.user.get_full_name() else obj.user.username

class UserSerializer(serializers.ModelSerializer):
    Date_Joined = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(write_only=True, default=datetime.now)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'Date_Joined', 'password', 'is_staff']
        extra_kwargs = {'password': {'write_only' : True}} 

    def get_Date_Joined(self, obj):
        return obj.date_joined.strftime('%Y-%m-%d')