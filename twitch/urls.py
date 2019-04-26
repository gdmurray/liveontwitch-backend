from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$', views.login, name='twitch_login'),
    url(r'^connect/$', views.connect, name="twitch_connect"),
    url(r'^auth/$', views.fetch_token, name='fetch_token'),
    url(r'^callback/$', views.callback, name='callback_twitch'),
    url(r'^logout/$', views.logout, name='twitch_logout'),
    url(r'^subscription/callback/$', views.TwitchSubscriptionEndpoint.as_view(), name="callback_subscribe_twitch"),
    url(r'^account/$', views.TwitchAccountInfo.as_view(), name='twitch_account_info')
]
