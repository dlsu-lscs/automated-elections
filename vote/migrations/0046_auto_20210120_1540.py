# Generated by Django 3.1.5 on 2021-01-20 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0045_auto_20201211_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='name',
            field=models.CharField(max_length=64, unique=True),
        )
    ]
