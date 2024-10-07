# Generated by Django 5.1.1 on 2024-10-07 16:11

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lennonapp', '0014_alter_cart_price_alter_cart_unit_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
    ]
