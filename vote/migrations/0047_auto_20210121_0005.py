# Generated by Django 3.1.2 on 2021-01-21 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0046_auto_20210120_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='serial_number',
            field=models.CharField(default=models.CharField(max_length=8, unique=True), max_length=10, unique=True),
        ),
    ]
