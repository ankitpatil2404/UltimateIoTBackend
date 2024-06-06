"""
code written by shubham waje
github -> https://www.github.com/wajeshubham
"""
from rest_framework import serializers
from django.shortcuts import get_object_or_404

from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.authtoken.models import Token


from .models import *

class RegisterUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self, **kwargs):
        user = User(
            username=self.validated_data['username'].lower(),
            email=self.validated_data['email'],
        )

        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError(
                {'status': status.HTTP_400_BAD_REQUEST, 'data': 'Passwords does not match'})
        user.set_password(password)
        user.save()
        return user

class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        label=_("password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:

            user=get_object_or_404(User,email=email)
            username=user.username

            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class tokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=50)


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)

    # token = serializers.CharField(
    #     min_length=1, write_only=True)
    # uidb64 = serializers.CharField(
    #     min_length=1, write_only=True)

    class Meta:
        fields = ['password']

    def validate(self, attrs):
        token = self.context['token']
        uidb64 = self.context['id']
        # print(token,uidb64)
        try:
            password = attrs.get('password')
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError({'error': 'The rest link is invalid'})

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise serializers.ValidationError({'error': 'The rest link is invalid'})
        return super().validate(attrs)