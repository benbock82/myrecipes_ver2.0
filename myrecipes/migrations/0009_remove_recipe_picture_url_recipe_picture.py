# Generated by Django 4.2.2 on 2023-06-28 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myrecipes', '0008_remove_recipe_cuisines_tag_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='picture_url',
        ),
        migrations.AddField(
            model_name='recipe',
            name='picture',
            field=models.ImageField(blank=True, upload_to='recipe/'),
        ),
    ]
