from django.urls import path
from .views import *

urlpatterns = [
    path('list/', ChannelView.as_view(), name='channel_list'),
    path('create/', create_channel, name='channel_creates'),
    path('<int:pk>/delete/', delete_channel, name='channel_delete'),
    path('<int:pk>/update/', update_channel, name='update_channel'),
    path('<int:pk>/reset_value/', reset_channel_values, name='reset_channel_values'),
    path('<int:pk>/', channel_details, name='channel_details'),
    path('<int:pk>/generate_read_api_key/', new_read_api_key, name='generate_read_api_key'),
    path('<int:pk>/generate_write_api_key/', new_write_api_key, name='generate_write_api_key'),
    path('read/API_KEY=<str:api_key>/', read_the_fields, name='read_the_fields'),
    path('write/API_KEY=<str:api_key>/', write_the_fields, name='write_the_fields'),
    path('contact/', send_query_mail, name="send_query_mail"),

]