# Generated by Django 5.0.6 on 2024-06-13 09:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bs_app', '0007_remove_cart_books'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='book',
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.DeleteModel(
            name='CartItem',
        ),
    ]
