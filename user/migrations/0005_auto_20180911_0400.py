# Generated by Django 2.0.6 on 2018-09-11 04:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20180911_0359'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Verifivation_code',
            new_name='Verification_code',
        ),
        migrations.RenameField(
            model_name='verification_code',
            old_name='verifivation_code',
            new_name='verification_code',
        ),
    ]