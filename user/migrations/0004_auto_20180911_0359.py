# Generated by Django 2.0.6 on 2018-09-11 03:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_verifivation_code'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Verification_code',
            new_name='Verifivation_code',
        ),
        migrations.RenameField(
            model_name='verifivation_code',
            old_name='verification_code',
            new_name='verifivation_code',
        ),
    ]