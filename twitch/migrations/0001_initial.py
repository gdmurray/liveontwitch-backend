# Generated by Django 2.2 on 2019-04-11 21:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import twitch.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TwitchAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=139, unique=True, verbose_name='uid')),
                ('extra_data', twitch.fields.JSONField(default=dict, verbose_name='extra data')),
                ('is_streaming', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='twitch', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'twitch account',
                'verbose_name_plural': 'twitch accounts',
            },
        ),
        migrations.CreateModel(
            name='OAuth2AccessToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField(help_text='access token (OAuth2)', verbose_name='token')),
                ('token_secret', models.TextField(blank=True, help_text='refresh token (OAuth2)', verbose_name='token secret')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='expires at')),
                ('account', models.OneToOneField(on_delete=models.Model, to='twitch.TwitchAccount')),
            ],
            options={
                'verbose_name': 'oauth2 application token',
                'verbose_name_plural': 'oauth2 application tokens',
            },
        ),
    ]
