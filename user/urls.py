from django.urls import path

from .views import *

urlpatterns = [
    path('register/', RegisterSiteUserView.as_view(), name='register'),
    path('login/', AuthToken.as_view(), name='login'),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(), name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('<uidb64>/<token>/password-reset-complete/', SetNewPasswordAPIView.as_view(),
         name='password-reset-complete'),
]
