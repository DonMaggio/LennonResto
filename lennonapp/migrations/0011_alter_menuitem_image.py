# Generated by Django 5.1.1 on 2024-09-12 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lennonapp', '0010_rename_quatity_orderitem_quantity_alter_cart_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='lennonapp/static/images'),
        ),
    ]
