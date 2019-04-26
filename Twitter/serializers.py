from rest_framework import serializers
from .models import TwitterAccount, LiveConfiguration, UsernameConfiguration, BioConfiguration


class AuthorizedTwitterAccountSerializer(serializers.ModelSerializer):
    active = serializers.SerializerMethodField()

    def get_active(self, obj):
        return obj.liveconfiguration.active

    class Meta:
        model = TwitterAccount
        fields = ('username', 'uid', 'active')


class ProfileContentSerializer(serializers.ModelSerializer):
    """
    For processing the twitter api json response
    """

    class Meta:
        model = TwitterAccount
        fields = ('name', 'verified', 'profile_image_url_https', 'description', 'updated')


class UsernameConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsernameConfiguration
        fields = ('id', 'live_text', 'active', 'positioning', 'updated')


class BioConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BioConfiguration
        fields = ('id', 'live_text', 'active', 'positioning', 'updated')


class TwitterConfigurationSerializer(serializers.ModelSerializer):
    username_config = serializers.SerializerMethodField()
    bio_config = serializers.SerializerMethodField()

    def get_username_config(self, obj):
        return UsernameConfigurationSerializer(obj.usernameconfiguration, many=False).data

    def get_bio_config(self, obj):
        return BioConfigurationSerializer(obj.bioconfiguration, many=False).data

    class Meta:
        model = LiveConfiguration
        fields = ('id', 'active', 'username_config', 'bio_config')


class ProfileDetailSerializer(serializers.ModelSerializer):
    config = serializers.SerializerMethodField()
    profile_image_url_https = serializers.SerializerMethodField()

    def get_config(self, obj):
        return TwitterConfigurationSerializer(obj.liveconfiguration, many=False).data

    def get_profile_image_url_https(self, obj):
        return obj.profile_image_url_https.replace("_normal.jpg", "_400x400.jpg")

    class Meta:
        model = TwitterAccount
        fields = ('name', 'username', 'uid', 'verified', 'updated',
                  'profile_image_url_https', 'config', 'description')
