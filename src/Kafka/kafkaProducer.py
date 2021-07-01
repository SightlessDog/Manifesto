# -*- coding: utf-8 -*-
import json
from kafka import KafkaProducer


class kafka_producer():

    def __init__(self, port, topic):
        self.bootstrap_servers = ['192.168.0.104:9092']
        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                      retries=5,
                                      value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                                      api_version=(0, 10, 1)
                                      )
        self.topicName = topic

    def send(self, message):
        ack = self.producer.send(self.topicName, message)
        metadata = ack.get()
        # print(metadata.topic)
        # print(metadata.partition)
