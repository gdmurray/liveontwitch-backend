# Generated by Django 2.2 on 2019-04-11 21:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Twitter', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='twitteraccount',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='twitter', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='oauth2accesstoken',
            name='account',
            field=models.OneToOneField(on_delete=models.Model, to='Twitter.TwitterAccount'),
        ),
    ]
