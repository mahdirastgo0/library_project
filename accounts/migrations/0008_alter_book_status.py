# Generated by Django 5.0.1 on 2025-03-12 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_author_bookstatus_genre_publisher_alter_user_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='status',
            field=models.CharField(choices=[('borrowed', 'borrowed'), ('sold', 'sold'), ('exist', 'exist')], default='exist', max_length=25),
        ),
    ]
