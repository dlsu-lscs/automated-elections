# Generated by Django 2.0.5 on 2018-07-01 07:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0008_remove_candidate_party'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='party',
            field=models.ForeignKey(default=0, null=True, on_delete=django.db.models.deletion.CASCADE, to='vote.Party'),
        ),
    ]
