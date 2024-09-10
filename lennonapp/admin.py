from django.contrib import admin

# Register your models here.
from .models import Category, MenuItem, Cart, Order, OrderItem


admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)

admin.site.site_header = 'Lennon Resto'
admin.site.index_title = 'Administrador de Resto'
admin.site.site_title = 'Lennon'