# Generated by Django 4.1 on 2024-09-12 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_remove_stamp_image_url_stamp_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diary',
            name='child',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.child'),
        ),
    ]
