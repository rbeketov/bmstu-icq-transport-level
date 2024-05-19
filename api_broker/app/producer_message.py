import json

from confluent_kafka import Producer

from .singletone import SingleTone


CONSUMER_TOPIC = "assembling_message_topic"


class KafkaMessageProducer(SingleTone):
    def __init__(self):
        self.producer = Producer({'bootstrap.servers': 'localhost:29092'})

    def _delivery_report(err, msg):
        """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))
    
    def produced_data(self, buffer: list[dict]):
        try:
            for data in buffer:
                self.producer.poll(0)
                json_data = json.dumps(data)
                self.producer.produce(
                    CONSUMER_TOPIC,
                    json_data.encode('utf-8'),
                    callback=self._delivery_report
                )
            self.producer.flush()
        except Exception as e:
            print("Cathced error while producing data")
