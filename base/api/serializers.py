from rest_framework.serializers import ModelSerializer
from base.models import Abstract


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Abstract

        fields = '__all__'
