# Generated by Django 4.1 on 2024-09-15 11:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_alter_children_household'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image_url',
            field=models.ImageField(blank=True, null=True, upload_to='profile_images/'),
        ),
        migrations.CreateModel(
            name='GrowthRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('height', models.FloatField()),
                ('weight', models.FloatField()),
                ('measurement_date', models.DateField()),
                ('memo', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.children')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'growth_records',
            },
        ),
    ]
