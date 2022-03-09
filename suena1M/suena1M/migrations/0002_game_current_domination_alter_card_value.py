# Generated by Django 4.0.2 on 2022-03-09 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suena1M', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='current_domination',
            field=models.CharField(choices=[('S', 'Solar'), ('W', 'Wind'), ('A', 'Atomic'), ('C', 'Carbon')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='card',
            name='value',
            field=models.IntegerField(choices=[(0, 'Neun'), (10, 'Zehn'), (2, 'Bube'), (3, 'Dame'), (4, 'King'), (11, 'Ass')]),
        ),
    ]
