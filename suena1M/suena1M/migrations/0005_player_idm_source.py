# Generated by Django 4.0.2 on 2022-03-15 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suena1M', '0004_player_last_played_round'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='idm_source',
            field=models.CharField(blank=True, choices=[('S', 'Solar'), ('W', 'Wind'), ('A', 'Atomic'), ('C', 'Carbon')], max_length=1, null=True),
        ),
    ]
