# Generated by Django 4.2.2 on 2023-06-27 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myrecipes', '0007_alter_recipe_cuisines_tag_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='cuisines_tag',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='ingredient_tag',
        ),
        migrations.AddField(
            model_name='recipe',
            name='cuisines_tag',
            field=models.ManyToManyField(to='myrecipes.cuisinetag'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredient_tag',
            field=models.ManyToManyField(to='myrecipes.ingredienttag'),
        ),
    ]
