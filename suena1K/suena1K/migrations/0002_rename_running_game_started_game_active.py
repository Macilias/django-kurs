# Generated by Django 4.0.2 on 2022-02-23 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suena1K', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='running',
            new_name='started',
        ),
        migrations.AddField(
            model_name='game',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]