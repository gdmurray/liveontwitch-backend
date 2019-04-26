from rest_framework import serializers
from .models import TwitchAccount


class TwitchAccountInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwitchAccount
        fields = ('partnered', 'email', 'logo')


class TwitchAccountDisplaySerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        return obj.user.username

    class Meta:
        model = TwitchAccount
        fields = ('username', 'uid', 'logo', 'partnered')
