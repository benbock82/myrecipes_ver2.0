# Generated by Django 4.2.2 on 2023-06-27 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myrecipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='picture_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='recipe',
            name='youtube_url',
            field=models.URLField(blank=True),
        ),
    ]
