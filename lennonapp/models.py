from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)

    def __str__(self) -> str:
        return f'{self.title}'
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=0, db_index=True)
    description = models.TextField(max_length=1000)
    #image = models.ImageField(upload_to='lennonapp/images', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    image = CloudinaryField('image', resource_type='image', blank=True, null=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'

#almacenamiento temporal del pedido (para agregar items antes de realizar el pedido)
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=0, default=0)
    price = models.DecimalField(max_digits=6, decimal_places=0, default=0)

    class Meta:
        unique_together = ('menuitem', 'user')

    def __str__(self):
        return f'{self.user} -> {self.menuitem}'

class Order(models.Model):
    user =models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="delivery_crew", null=True)
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=0)
    date= models.DateField(db_index=True)

    def __str__(self):
        return f'{self.user} Total: {self.total} ({self.pk})'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=0)
    price = models.DecimalField(max_digits=6, decimal_places=0)

    def __str__(self):
        return f'{self.menuitem}'

    class Meta:
        unique_together = ('order', 'menuitem')
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"