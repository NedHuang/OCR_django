# Generated by Django 2.0.6 on 2018-07-23 07:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_auto_20180723_0740'),
    ]

    operations = [
        migrations.RenameField(
            model_name='share',
            old_name='file',
            new_name='shared_file',
        ),
    ]
