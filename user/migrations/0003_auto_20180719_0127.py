# Generated by Django 2.0.6 on 2018-07-19 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20180718_1005'),
    ]

    operations = [
        migrations.AddField(
            model_name='object',
            name='content',
            field=models.CharField(default='', max_length=256),
        ),
        migrations.AlterField(
            model_name='object',
            name='categoty',
            field=models.CharField(default='', max_length=256),
        ),
    ]