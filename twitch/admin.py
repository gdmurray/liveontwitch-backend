from django.contrib import admin

from twitch.models import TwitchAccount, OAuth2AccessToken, \
    TwitchSubscription, TwitchEvent
from twitch.tasks import twitch_subscribe_webhook


class TwitchAccountAdmin(admin.ModelAdmin):
    search_fields = ['user']
    raw_id_fields = ('user',)
    list_display = ('user', 'uid')


class OAuth2AccessTokenAdmin(admin.ModelAdmin):
    raw_id_fields = ('account',)
    list_display = ('account', 'truncated_token', 'expires_at')
    list_filter = ('expires_at',)

    def truncated_token(self, token):
        max_chars = 40
        ret = token.token
        if len(ret) > max_chars:
            ret = ret[0:max_chars] + '...(truncated)'
        return ret

    truncated_token.short_description = 'Token'


def re_subscribe(modeladmin, request, queryset):
    for subscription in queryset:
        twitch_subscribe_webhook(subscription.account.uid)


re_subscribe.short_description = "Resubscribe to webhook"


class TwitchSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('account', 'subscription_date', 'expiry', 'confirmed')
    actions = (re_subscribe,)


class TwitchEventAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'action', 'created')


admin.site.register(TwitchEvent, TwitchEventAdmin)
admin.site.register(TwitchSubscription, TwitchSubscriptionAdmin)
admin.site.register(TwitchAccount, TwitchAccountAdmin)
admin.site.register(OAuth2AccessToken, OAuth2AccessTokenAdmin)
