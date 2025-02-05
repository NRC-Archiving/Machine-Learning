from kafka import KafkaProducer
import json

class KafkaProducerClient:
    def __init__(self, bootstrap_servers, topic, serializer=None):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.serializer = serializer or (lambda x: json.dumps(x).encode('utf-8'))
        self.producer = KafkaProducer(
            bootstrap_servers = self.bootstrap_servers,
            value_serializer = self.serializer
        )
        print("Kafka broker initialized")
    
    def send_result(self, success, result):
        message = {"success":success,"message":result}
        try:
            self.producer.send(self.topic, value=message)
            self.producer.flush()
            print("Result sent to broker")
        except Exception as e:
            print(f"Error while sending message: {e}")

    def close(self):
        if self.producer:
            self.producer.close()
            print("KafkaProducer connection closed")