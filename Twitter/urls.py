from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^login/?$', TwitterLogin.as_view(), name="twitter_login"),
    url(r'^accounts/?$', TwitterAccounts.as_view(), name="accounts_list"),
    url(r'^callback/?$', twitter_authenticated, name="twitter_callback"),
    url(r'^(?P<uid>[\w\-]+)/?$', TwitterConfiguration.as_view(), name="twitter-configuration"),
]
