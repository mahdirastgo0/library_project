# Generated by Django 5.0.1 on 2025-03-15 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_alter_book_discounted_price_alter_book_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=255, unique=True, verbose_name='آدرس ایمیل'),
        ),
    ]
