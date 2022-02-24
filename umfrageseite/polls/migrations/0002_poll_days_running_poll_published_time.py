# Generated by Django 4.0.2 on 2022-02-07 13:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='days_running',
            field=models.IntegerField(default=7),
        ),
        migrations.AddField(
            model_name='poll',
            name='published_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]