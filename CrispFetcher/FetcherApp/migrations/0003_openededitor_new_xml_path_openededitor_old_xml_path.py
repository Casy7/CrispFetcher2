# Generated by Django 5.0.4 on 2024-04-24 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FetcherApp', '0002_openededitor_delete_userinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='openededitor',
            name='new_XML_path',
            field=models.TextField(blank=True, max_length=3000),
        ),
        migrations.AddField(
            model_name='openededitor',
            name='old_XML_path',
            field=models.TextField(blank=True, max_length=3000),
        ),
    ]
