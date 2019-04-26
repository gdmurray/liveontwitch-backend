# Generated by Django 2.2 on 2019-04-26 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Twitter', '0009_twitteraccount_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='twitteraccount',
            name='modified_bio',
            field=models.CharField(blank=True, max_length=600, null=True),
        ),
        migrations.AddField(
            model_name='twitteraccount',
            name='modified_hold',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='twitteraccount',
            name='modified_name',
            field=models.CharField(blank=True, max_length=140, null=True),
        ),
    ]
