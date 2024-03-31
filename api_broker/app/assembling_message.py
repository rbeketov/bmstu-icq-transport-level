import threading
import time

from confluent_kafka import Consumer

from confluent_kafka.admin import AdminClient, NewTopic


GET_MESSAGE_INTERVAL = 5
BOOTSTRAP_SERVER = 'localhost:29092'
CONSUMER_TOPIC = "assembling_message_topic"
GROUP_ID = "assembling_message_id"
AUTO_OFFSET_RESET = 'earliest'


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

                result_messages.append(msg.value().decode('utf-8'))

        except Exception as e:
            print(f"Error: {e}")
            return []

        return result_messages

    def process_messages(self, messages):
        for message in messages:
            print(message)


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