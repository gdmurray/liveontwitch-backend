# Generated by Django 2.2 on 2019-04-12 16:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twitch', '0002_auto_20190412_1605'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='twitchaccount',
            name='is_streaming',
        ),
    ]
