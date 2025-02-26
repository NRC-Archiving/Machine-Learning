from kafka import KafkaProducer
import json

class KafkaProducerClient:
    def __init__(self, bootstrap_servers, topic=None, serializer=None):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.serializer = serializer or (lambda x: json.dumps(x).encode('utf-8'))
        self.producer = KafkaProducer(
            bootstrap_servers = self.bootstrap_servers,
            value_serializer = self.serializer
        )
        print("Kafka Producer initialized")
    
    def send_result(self, success, result, topic=None):
        if topic is None and self.topic is None:
            raise ValueError("Topic must be initialized either in constructor or in send_result method.")

        message = {"success":success,"message":result}
        try:
            self.producer.send(topic or self.topic, value=message)
            self.producer.flush()
            print(f"Message sent to broker: [topic: ${topic or self.topic}]")
        except Exception as e:
            print(f"Error while sending message: {e}")

    def close(self):
        if self.producer:
            self.producer.close()
            print("KafkaProducer connection closed")