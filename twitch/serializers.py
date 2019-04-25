from rest_framework import serializers
from .models import TwitchAccount


class TwitchAccountInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwitchAccount
        fields = ('partnered', 'email', 'logo')
