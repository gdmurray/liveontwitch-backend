# Generated by Django 2.2 on 2019-04-13 04:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_temporarytoken_text'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='temporarytoken',
            name='provider',
        ),
        migrations.RemoveField(
            model_name='temporarytoken',
            name='text',
        ),
    ]
