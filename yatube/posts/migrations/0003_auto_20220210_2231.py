# Generated by Django 2.2.9 on 2022-02-10 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20220207_1954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(blank=True, max_length=2500, null=True),
        ),
    ]
