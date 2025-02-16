from kafka import KafkaConsumer
import json
import threading

class KafkaConsumerClient:
    def __init__(self, topic, bootstrap_servers, deserializer=None):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.deserializer = deserializer or (lambda x: json.loads(x.decode('utf-8')))
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            value_deserializer=self.deserializer
        )
        self.running = False
        print(f"Kafka Consumer initialized for topic: {self.topic}")

    def start_listening(self, callback):
        if self.running:
            print("Consumer is already running!")
            return
        
        self.running = True

        def consume():
            try:
                for message in self.consumer:
                    data = message.value
                    print(f"Received from broker: [topic: ${self.topic}]")
                    callback(data)
            except Exception as e:
                print(f"Error while consuming messages: {e}")

        thread = threading.Thread(target=consume, daemon=True)
        thread.start()

    def stop_listening(self):
        self.running = False
        self.consumer.close()
        print(f"Kafka Consumer for topic {self.topic} closed")
