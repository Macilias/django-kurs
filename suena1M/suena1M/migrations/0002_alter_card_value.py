# Generated by Django 4.0.2 on 2022-03-04 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suena1M', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='value',
            field=models.IntegerField(choices=[(0, 'Neun'), (10, 'Zehn'), (2, 'Jack'), (3, 'Dame'), (4, 'King'), (11, 'Ass')]),
        ),
    ]
