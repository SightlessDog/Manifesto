from kafka import KafkaProducer

bootstrap_servers = ['localhost:9092']
topicName = 'raspi1'

producer = KafkaProducer(bootstrap_servers = bootstrap_servers, retries = 5)

while True:
    ack = producer.send(topicName, b'Hello from python')
    metadata = ack.get()
    print(metadata.topic)
    print(metadata.partition)
