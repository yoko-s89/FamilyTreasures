# Generated by Django 4.1 on 2024-09-14 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_diary_child'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='diarymedia',
            name='media_url',
        ),
        migrations.AddField(
            model_name='diarymedia',
            name='media_file',
            field=models.FileField(default='', upload_to='diary_media/'),
            preserve_default=False,
        ),
    ]
