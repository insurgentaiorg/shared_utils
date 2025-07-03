import os
import json
from quixstreams import Application, ProduceToTopic

class KafkaClient:
    def __init__(self):
        self.broker_address = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.client_id = os.getenv("KAFKA_CLIENT_ID", "default-client")
        self._app = None
        self._producer = None

    @property
    def app(self):
        if self._app is None:
            self._app = Application(
                broker_address=self.broker_address,
                client_id=self.client_id,
            )
        return self._app

    @property
    def producer(self) -> ProduceToTopic:
        if self._producer is None:
            # this is lazily initialized to a topic-specific producer
            self._producer = {}
        return self._producer

    def send(self, topic: str, value: dict, key: str | None = None):
        if topic not in self.producer:
            topic_obj = self.app.topic(topic)
            self.producer[topic] = topic_obj.get_producer(value_serializer=json.dumps)

        self.producer[topic].produce(value, key=key)

    def flush(self):
        for producer in self.producer.values():
            producer.flush()


kafka_client = KafkaClient()  # module level singleton instance 
