from kafka import KafkaProducer
bootstrap_servers = ['localhost:9092']
topicName = 'myTopic'
producer = KafkaProducer(bootstrap_servers = bootstrap_servers)

ack = producer.send(topicName, b'Hello World!!!!!!!!')
metadata = ack.get()
print(metadata.topic)
print(metadata.partition)