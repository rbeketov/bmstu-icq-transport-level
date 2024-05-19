import threading
import time
import json
import requests

from confluent_kafka import Consumer

from confluent_kafka.admin import AdminClient, NewTopic


GET_MESSAGE_INTERVAL = 3
BOOTSTRAP_SERVER = 'localhost:29092'
CONSUMER_TOPIC = "assembling_message_topic"
GROUP_ID = "assembling_message_id"
AUTO_OFFSET_RESET = 'earliest'
URL_RECIVE ="http://localhost:8082/recive/"


class KafkaMessageConsumer(threading.Thread):
    def __init__(self, interval):
        threading.Thread.__init__(self)
        
        self.interval = interval

        self.consumer = Consumer({
            'bootstrap.servers': BOOTSTRAP_SERVER,
            'group.id': GROUP_ID,
            'auto.offset.reset': AUTO_OFFSET_RESET
        })
        self.consumer.subscribe([CONSUMER_TOPIC])

    def run(self):
        while True:
            messages = self.get_messages_from_kafka()
            self.process_messages(messages)
            time.sleep(self.interval)

    def get_messages_from_kafka(self):
        result_messages = []
        try: 
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    break
                if msg.error():
                    print("Consumer error: {}".format(msg.error()))
                    break
                
                json_data = json.loads(msg.value().decode('utf-8'))
                result_messages.append(json_data)
        except Exception as e:
            print(f"Error: {e}")
            return []

        return result_messages

    def process_messages(self, messages): 
        sorted_messages = sorted(messages, key=lambda x: (x['timestamp'], x['part_message_id']))
        
        result_message = []
        
        prev_timestamp = None
        curr_sender = None
        curr_message = None

        prev_id = None
        flag_error = False
        
        for message in sorted_messages:

            if prev_timestamp == message['timestamp']:
                curr_message += message['message']
                if prev_id + 1 != message['part_message_id']:
                    flag_error = True
                prev_id = message['part_message_id']
            else:
                if prev_timestamp is not None:
                    result_message.append(
                        {
                            "sender": curr_sender,
                            "timestamp": prev_timestamp,
                            "message": curr_message,
                            "flag_error": flag_error,
                        }
                    )
                flag_error = False
                prev_id = message['part_message_id']
                if prev_id != 1:
                    flag_error = True
                prev_timestamp = message['timestamp']
                curr_message = message['message']
                curr_sender = message['sender']

        for mes in result_message:
            response = requests.post(URL_RECIVE, data=mes)
            if response.status_code != 200:
                print(f"Получен статуc {response.status_code} от сервера кодирования")


def assembling_message():
    a = AdminClient({'bootstrap.servers': BOOTSTRAP_SERVER})

    new_topics = [NewTopic(topic, num_partitions=3, replication_factor=1) for topic in [CONSUMER_TOPIC]]
    fs = a.create_topics(new_topics)
    for topic, f in fs.items():
        try:
            f.result()
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))

    kafka_consumer = KafkaMessageConsumer(interval=GET_MESSAGE_INTERVAL)
    kafka_consumer.start()