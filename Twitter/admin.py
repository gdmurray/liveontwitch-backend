from django.contrib import admin

from .models import TwitterAccount, OAuth2AccessToken, \
    BioConfiguration, UsernameConfiguration, LiveConfiguration


class TwitterAccountAdmin(admin.ModelAdmin):
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


class BioConfigInline(admin.TabularInline):
    fields = ('active', 'live_text', 'positioning', 'updated')
    readonly_fields = ('updated',)
    model = BioConfiguration


class UsernameConfigInline(admin.TabularInline):
    fields = ('active', 'live_text', 'positioning', 'updated')
    readonly_fields = ('updated',)
    model = UsernameConfiguration


class ConfigurationAdmin(admin.ModelAdmin):
    inlines = (BioConfigInline, UsernameConfigInline)
    list_display = ('user', 'account')


admin.site.register(LiveConfiguration, ConfigurationAdmin)
admin.site.register(OAuth2AccessToken, OAuth2AccessTokenAdmin)
admin.site.register(TwitterAccount, TwitterAccountAdmin)
