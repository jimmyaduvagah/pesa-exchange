# Generated by Django 3.2.4 on 2021-06-20 20:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20210620_1928'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='id_number',
        ),
    ]
