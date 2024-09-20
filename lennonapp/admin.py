from django.contrib import admin

# Register your models here.
from .models import Category, MenuItem, Cart, Order, OrderItem


admin.site.register(Category)
#admin.site.register(MenuItem)
admin.site.register(Cart)
#admin.site.register(Order)
#admin.site.register(OrderItem)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ["title", "price", "category"]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "menuitem", "quantity", "unit_price", "price"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["OrderNumber", "user", "delivery_crew", "status", "total", "date"]

    def OrderNumber(self, obj):
        return  "Order "+ f'{obj.pk}'

    OrderNumber.short_description = "Order Number"


admin.site.site_header = 'Lennon Resto'
admin.site.index_title = 'Administrador de Resto'
admin.site.site_title = 'Lennon'
