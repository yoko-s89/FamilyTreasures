# Generated by Django 4.1 on 2024-09-12 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_weather_diary_weather'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stamp',
            name='image_url',
        ),
        migrations.AddField(
            model_name='stamp',
            name='image',
            field=models.ImageField(default='stamps/default.png', upload_to='stamps/'),
            preserve_default=False,
        ),
    ]
