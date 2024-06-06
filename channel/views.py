"""
code written by shubham waje
github -> https://www.github.com/wajeshubham
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_key import Key
from .serializers import *

# TODO CRAFT MAIL TEMPLATE

key = Key('aaaa-bbbb-cccc-dddd-1111')


class ChannelView(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get(request):
        channel = Channel.objects.filter(user=request.user).order_by('-created_at')
        serializer = ChannelSerializer(channel, many=True)
        data = {
            'status': status.HTTP_200_OK,
            'data': serializer.data
        }
        return Response(data)


# TODO sending two post req
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_channel(request):
    Channel.objects.create(user=request.user,
                           name=request.data['name'],
                           description=request.data['description'],
                           fields=request.data['fields'].split(','),
                           values=[-999999999 for x in range(16)],  # initially field values are -999999999 (random value)
                           read_api_key=Key(),
                           write_api_key=Key()
                           )
    data = {
        'status': status.HTTP_201_CREATED,
        'message': 'channel has been created.'
    }
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_channel(request, **kwargs):
    channel = get_object_or_404(Channel, id=kwargs.get('pk'))
    if 'name' in request.data and channel.name != request.data['name']:
        channel.name = request.data['name']
    if 'description' in request.data and channel.description != request.data['description']:
        channel.description = request.data['description']
    if 'fields' in request.data and channel.fields != request.data['fields']:
        lst = []
        val_lst = []
        rem_val = channel.values + [-999999999 for _ in range(len(channel.values),16)]
        for i in range(len(request.data['fields'].split(','))):
            if request.data['fields'].split(',')[i] != "":
                lst.append(request.data['fields'].split(',')[i])
                val_lst.append(rem_val[i])
                channel.values.append(-999999999)  # when we update we need to increase length of values list to keep it in sync
            else:
                pass
        channel.fields = lst
        channel.values = val_lst
    channel.save()
    data = {
        'status': status.HTTP_200_OK,
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def channel_details(request, **kwargs):
    channel = get_object_or_404(Channel, id=kwargs.get('pk'))
    if channel.user == request.user:
        serializer = ChannelSerializer(channel, many=False)
        data = {
            'status': status.HTTP_200_OK,
            'data': serializer.data,
            'field_list': channel.fields
        }

        return Response(data)
    else:
        data = {
            'status': status.HTTP_200_OK,
            'data': "channel does not exist",

        }

        return Response(data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_channel(request, **kwargs):
    channel = get_object_or_404(Channel, id=kwargs.get('pk'))
    if channel.user == request.user:
        channel.delete()
        data = {
            'status': status.HTTP_200_OK,
            'data': 'channel has been deleted'
        }

        return Response(data)
    else:
        data = {
            'status': status.HTTP_200_OK,
            'data': 'channel does not exist'
        }

        return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_read_api_key(request, **kwargs):
    channel = get_object_or_404(Channel, id=kwargs.get('pk'))
    if channel.user == request.user:
        channel.read_api_key = Key()
        channel.save()
        serializer = ChannelSerializer(channel, many=False)
        data = {
            'status': status.HTTP_200_OK,
            'data': serializer.data
        }

        return Response(data)
    else:
        data = {
            'status': status.HTTP_200_OK,
            'data': 'something went wrong'
        }

        return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_write_api_key(request, **kwargs):
    channel = get_object_or_404(Channel, id=kwargs.get('pk'))
    if channel.user == request.user:
        channel.write_api_key = Key()
        channel.save()
        serializer = ChannelSerializer(channel, many=False)
        data = {
            'status': status.HTTP_200_OK,
            'data': serializer.data
        }

        return Response(data)
    else:
        data = {
            'status': status.HTTP_200_OK,
            'data': 'something went wrong'
        }

        return Response(data)


@api_view(['GET'])
def read_the_fields(request, **kwargs):
    channel = get_object_or_404(Channel, read_api_key=kwargs.get("api_key"))
    if channel.name:
        serializer = ReadChannelSerializer(channel, many=False)
        data = {
            'status': status.HTTP_200_OK,
            'data': serializer.data
        }
        return Response(data)
    else:
        data = {
            'status': status.HTTP_200_OK,
            'data': "channel does not exist"
        }

        return Response(data)


@api_view(["GET"])
def write_the_fields(request, **kwargs):
    channel = get_object_or_404(Channel, write_api_key=kwargs.get("api_key"))
    s = request.query_params
    lst = channel.values
    try:
        """
        we will try if there are any queries in url we will extract them and assign the values associated with it'
        to the respective index of lst[] 
        and if there are no fields available in url 
        we will assign values of channel.values to the respective index of lst
        and if we don't have values at channel.values[i] we will simply assign 0 to respective index if lst[]
        """
        for i in range(16):
            try:
                if s[f'field{i + 1}']:
                    lst[i] = s[f'field{i + 1}']
            except:
                if channel.values[i]:
                    lst[i] = channel.values[i]
                else:
                    lst[i] = -999999999
    except:
        pass

    if len(lst) <= len(channel.fields):
        for i in range(len(channel.fields) - 1):
            """if the channel values are not equal to the lst values the we will pass so that we will avoid the 
            following bug:
             lst=[76,87,80,0,0,0] channel.values=[20,30,40,54,76,0] in above care the value of lst[3] is 0 and 
             value of channel.values[3] is 54 so 
             if we use expression channel.values[i] = lst[i] here the 
             channel.values[3] will become 0 which we don't want """
            print(i, channel.values, channel.fields)

            if channel.values[i] != lst[i]:
                pass
            else:
                channel.values[i] = lst[i]
    else:
        channel.values = lst[:len(channel.fields)]
    channel.save()
    serializer = ChannelSerializer(channel, many=False)

    data = {'data': "success"}
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_channel_values(request, **kwargs):
    channel = get_object_or_404(Channel, id=kwargs.get("pk"))
    channel.values = [-999999999 for _ in range(16)]
    channel.save()
    serializer = ChannelSerializer(channel, many=False)

    data = {'data': serializer.data, 'message': "'values are successfully reset'", 'fields': channel.fields}
    return Response(data)


@api_view(['POST'])
def send_query_mail(request):
    print("----------->", request.data['full_name'])
    print("----------->", request.data['email'])
    print("----------->", request.data['phone'])
    print("----------->", request.data['enquiry_for'])
    print("----------->", request.data['org_name'])
    print("----------->", request.data['message'])
    print("----------->", request.data['country'])
    # # mail for authority
    # send_mail("Enquiry mail", request.data["message"], "**sender's mail**", ["waje.shubham111@gmail.com"],
    #           fail_silently=False)
    #
    # # mail for user
    # send_mail("Thanks for contacting us!", "We appreciate your response, we will get back to you very soon.",
    #           "**sender's mail**", [request.data["email"]],
    #           fail_silently=False
    data = {'status': status.HTTP_200_OK, 'data': "We've got your message. Thanks for contacting us."}
    return Response(data)
