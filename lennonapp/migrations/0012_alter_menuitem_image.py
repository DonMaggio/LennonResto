# Generated by Django 5.1.1 on 2024-09-12 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lennonapp', '0011_alter_menuitem_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='lennonapp/images'),
        ),
    ]
