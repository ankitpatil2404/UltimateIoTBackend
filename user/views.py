"""
code written by shubham waje
github -> https://www.github.com/wajeshubham
"""

from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail as sm
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *


# Create your views here.


# TODO password reset done Email verification remaining


class AuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        print("-------------->")
        print(request.data)
        data = {}
        # request.data['username'] = request.data['username'].lower()
        serializer = AuthTokenSerializer(data=request.data,
                                         context={'request': request})

        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            token, created = Token.objects.get_or_create(user=user)

            data['status'] = status.HTTP_200_OK
            data['data'] = {}
            data['data']['token'] = token.key
            data['data']['user_id'] = user.pk
            data['data']['username'] = user.username
            data['data']['email'] = user.email

            return Response(data)
        else:
            return Response(
                {"data": 'Unable To Login With Provided Credentials', 'status': status.HTTP_400_BAD_REQUEST})


class RegisterSiteUserView(APIView):

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        data = {}
        if request.data['username'] == "":
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Username required'})
        if request.data['email'] == "":
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Email required'})
        if request.data['password'] == ".":
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Enter a valid password'})
        if request.data['password2'] == ".":
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Enter a valid password'})

        if (User.objects.filter(username=request.data['username'].lower()).count()) > 0:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Username Already Exists'})
        if (User.objects.filter(email=request.data['email']).count()) > 0:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'This Email Is Already Being Used'})
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get_or_create(user=user)

            data['status'] = status.HTTP_201_CREATED
            data['data'] = {
                'info': serializer.data,
                'token': Token.objects.get(user=user).key
            }
            print("-------------->")
            print(data)
        else:
            data['status'] = status.HTTP_400_BAD_REQUEST
            data['data'] = serializer.errors
        return Response(data)


# in this function we are just taking email from user and sending password reset mail to that mail
class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            absurl = f'http://127.0.0.1:8000/api/user/password-reset/{uidb64}/{token}'
            email_body = 'Hello, \n Use link below to reset your password  \n' + absurl
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            sm(
                subject='Reset Password',
                message=email_body,
                from_email='abc@gmail.com', # TODO senders mail id
                recipient_list=[data['to_email']],
                fail_silently=False,
            )
            return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        else:
            return Response({'Abort': 'Mail is not matching with your mail'}, status=status.HTTP_400_BAD_REQUEST)


""" in this function we are accepting the link which we sent in the mail
 with uidb64 and token and we are decoding them and sending decoded uidb64"""


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'},
                                status=status.HTTP_401_UNAUTHORIZED)

            return redirect('http://localhost:3000/user/password-reset/' + urlsafe_base64_encode(smart_bytes(
                id)) + '/' + token)

        except DjangoUnicodeDecodeError as identifier:
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'},
                                status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordAPIView(generics.GenericAPIView):
    """In this we are actually taking passwords from user and reseting it"""
    serializer_class = SetNewPasswordSerializer

    def patch(self, request, uidb64, token):
        if request.data['password'] == ".":
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Enter a valid password'})
        if request.data['password2'] == ".":
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'data': 'Enter a valid password'})

        serializer = self.serializer_class(data={'password': request.data['password']},
                                           context={'id': uidb64, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)
