from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin

from .models import User, TemporaryToken
from twitch.models import TwitchAccount
from Twitter.models import TwitterAccount


# Register your models here.
class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class TwitchAccountInline(admin.TabularInline):
    model = TwitchAccount
    fields = ('uid', 'extra_data')


class TwitterAccountInline(admin.TabularInline):
    model = TwitterAccount
    fields = ('username', 'uid')


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    inlines = (TwitchAccountInline, TwitterAccountInline)


class TemporaryTokenAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, MyUserAdmin)
admin.site.register(TemporaryToken, TemporaryTokenAdmin)
