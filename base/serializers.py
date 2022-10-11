from rest_framework import serializers
from .models import User, Topic, Abstract, Message


class AbstractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Abstract
        fields = ['__all__']


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['__all__']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        Model = User
        fields = ['__all__']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        Model = Message
        fields = ['__all__']
