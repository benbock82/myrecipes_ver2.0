# Generated by Django 4.2.2 on 2023-06-27 06:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myrecipes', '0004_recipe_cuisines'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='cuisines',
        ),
    ]
