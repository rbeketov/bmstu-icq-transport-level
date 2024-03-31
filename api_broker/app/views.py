from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from kafka import KafkaProducer


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('sender',
                          openapi.IN_QUERY,
                          description="ID отправителя сообщения",
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter('timestamp',
                          openapi.IN_QUERY,
                          description="Время отправления",
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter('message',
                          openapi.IN_QUERY,
                          description="Сообщение",
                          type=openapi.TYPE_INTEGER),
    ],
    responses={
        200: "Ок",
        400: "Ошибка в запросе",
    },
)
@api_view(['POST'])
def send_message(request, format=None):

    return Response(status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('sender',
                          openapi.IN_QUERY,
                          description="ID отправителя сообщения",
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter('timestamp',
                          openapi.IN_QUERY,
                          description="Время отправления",
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter('part_message_id',
                          openapi.IN_QUERY,
                          description="ID части сообщения",
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter('message',
                          openapi.IN_QUERY,
                          description="Часть сообщения",
                          type=openapi.TYPE_INTEGER),
    ],
    responses={
        200: "Ок",
        400: "Ошибка в запросе",
    },
)
@api_view(['POST'])
def transfer_message(request, format=None):

    return Response(status=status.HTTP_200_OK)
