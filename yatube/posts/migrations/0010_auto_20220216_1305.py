# Generated by Django 2.2.9 on 2022-02-16 13:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_group_create_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='create_date',
        ),
        migrations.RemoveField(
            model_name='group',
            name='user',
        ),
    ]
