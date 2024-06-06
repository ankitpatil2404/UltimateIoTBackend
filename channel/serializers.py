"""
code written by shubham waje
github -> https://www.github.com/wajeshubham
"""
from rest_framework import serializers

from .models import *


class ChannelSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%B %d %Y")
    data = serializers.SerializerMethodField()
    class Meta:
        model = Channel
        fields = ['id', 'user', 'name', 'description', 'created_at', 'read_api_key', 'write_api_key', 'data']

    @staticmethod
    def get_data(obj):
        data = {}
        for i in range(len(obj.fields)):
            try:
                data[str(obj.fields[i])] = obj.values[i]
            except:
                data[str(obj.fields[i])] = -999999999
        return data

    @staticmethod
    def get_user(obj):
        return obj.user.username


class ReadChannelSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%B %d %Y, %I:%M %p")
    data = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = ['id', 'user', 'name', 'description', 'created_at', 'data']

    @staticmethod
    def get_data(obj):
        data = {}
        for i in range(len(obj.fields)):
            try:
                data[str(obj.fields[i])] = {f'field{i + 1}': obj.values[i]}
            except:
                data[str(obj.fields[i])] = {f'field{i + 1}': -999999999}
        return data

    @staticmethod
    def get_user(obj):
        return obj.user.username
