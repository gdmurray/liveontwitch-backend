# Generated by Django 2.2 on 2019-04-12 16:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.OAUTH2_PROVIDER_APPLICATION_MODEL),
        ('core', '0002_auto_20190412_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='temporarytoken',
            name='application',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL),
        ),
    ]
