# Generated by Django 5.1.1 on 2024-09-05 19:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lennonapp', '0003_alter_menuitem_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='lennonapp/files/images'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='menuitem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='lennonapp.menuitem'),
        ),
    ]
