
import json
import requests
from itertools import islice

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from strenum import StrEnum
from enum import auto

from .producer_message import KafkaMessageProducer

from kafka import KafkaProducer
from .logger import Logger


LEN_BYTES = 100
URL_CODING_SERVICE = "http://localhost:8081/code/"
logger = Logger().get_logger(__name__)


def batched(iterable, n):
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch

class RequestField(StrEnum):
    sender = auto()
    timestamp = auto()
    message = auto()
    part_message_id = auto()
    flag_error = auto()

@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'sender',
            openapi.IN_QUERY,
            description="login отправителя сообщения",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'timestamp',
            openapi.IN_QUERY,
            description="Время отправления",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'message',
            openapi.IN_QUERY,
            description="Сообщение",
            type=openapi.TYPE_INTEGER
        ),
    ],
    responses={
        200: "Ок",
        400: "Ошибка в запросе",
    },
)
@api_view(['POST'])
def send_message(request, format=None):

    data = json.loads(request.body.decode())

    request_sender = data.get(RequestField.sender, "")
    if not request_sender or not isinstance(request_sender, str):

        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"Ошибка": f"Ошибка в поле {RequestField.sender}"}
        )
    request_timestamp = data.get(RequestField.timestamp, "")
    if not request_timestamp or not isinstance(request_timestamp, int):
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"Ошибка": f"Ошибка в поле {RequestField.timestamp}"}
        )
    request_message = data.get(RequestField.message, "")
    if not request_message or not isinstance(request_message, str):
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"Ошибка": f"Ошибка в поле {RequestField.message}"}
        )
        err_mess = f"Ошибка в поле {RequestField.sender}"
        logger.error(err_mess)
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"Ошибка": err_mess}
        )
    request_timestamp = data.get(RequestField.timestamp, "")
    if not request_timestamp or not isinstance(request_timestamp, int):
        err_mess = f"Ошибка в поле {RequestField.timestamp}"
        logger.error(err_mess)
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"Ошибка": err_mess}
        )
    request_message = data.get(RequestField.message, "")
    if not request_message or not isinstance(request_message, str):
        err_mess = f"Ошибка в поле {RequestField.message}"
        logger.error(err_mess)
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"Ошибка": err_mess}
        )
    
    #TODO отравлять только байты
    result_dicts = []
    try:
        request_message_bytes = bytes(request_message.encode('utf-8'))
        for i, batch in enumerate(batched(request_message_bytes, LEN_BYTES)):
            result_dicts.append(
                {
                    "sender": request_sender,
                    "timestamp": request_timestamp,
                    "part_message_id": i,
                    "message": batch.decode('utf-8'),
                }
            )
    except Exception as e:
        logger.error(f"Ошибка во время сегментации и декодирования: {e}")
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    for d in result_dicts:
        response = requests.post(URL_CODING_SERVICE, data=d)
        if response.status_code != 200:
            logger.error(f"Получен статуc {response.status_code} от сервера кодирования")


    logger.info("Запрос обработан со статусом 200")
    return Response(status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'sender',
            openapi.IN_QUERY,
            description="login отправителя сообщения",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'timestamp',
            openapi.IN_QUERY,
            description="Время отправления",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'part_message_id',
            openapi.IN_QUERY,
            description="ID части сообщения",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'message',
            openapi.IN_QUERY,
            description="Часть сообщения",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'flag_error',
            openapi.IN_QUERY,
            description="Признак ошибки",
            type=openapi.TYPE_BOOLEAN
        ),
    ],
    responses={
        200: "Ок",
        400: "Ошибка в запросе",
    },
)
@api_view(['POST'])
def transfer_message(request, format=None):
    try:
        data = json.loads(request.body.decode())

        request_sender = data.get(RequestField.sender, "")
        if not request_sender or not isinstance(request_sender, str):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"Ошибка": f"Ошибка в поле {RequestField.sender}"}
            )
        request_timestamp = data.get(RequestField.timestamp, "")
        if not request_timestamp or not isinstance(request_timestamp, int):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"Ошибка": f"Ошибка в поле {RequestField.timestamp}"}
            )
        request_message = data.get(RequestField.message, "")
        if not request_message or not isinstance(request_message, str):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"Ошибка": f"Ошибка в поле {RequestField.message}"}
            )
        request_part_message_id = data.get(RequestField.part_message_id, "")
        if not request_part_message_id or not isinstance(request_part_message_id, int):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"Ошибка": f"Ошибка в поле {RequestField.part_message_id}"}
            )
        request_flag_error = data.get(RequestField.flag_error, "")
        if request_flag_error == "" or not isinstance(request_flag_error, bool):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"Ошибка": f"Ошибка в поле {RequestField.flag_error}"}
            )

        producer = KafkaMessageProducer()
        producer.produced_data([data])
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"Ошибка": f"{e}"})

