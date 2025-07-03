import os
import json
from quixstreams import Application, ProduceToTopic

class KafkaClient:
    def __init__(self):
        self.broker_address = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.client_id = os.getenv("KAFKA_CLIENT_ID", "default-client")
        self._app = None
        self._producers = {}  # dict[str, ProduceToTopic]

    @property
    def app(self):
        if self._app is None:
            self._app = Application(
                broker_address=self.broker_address,
                client_id=self.client_id,
            )
        return self._app

    def send(self, topic: str, value: dict, key: str | None = None):
        if topic not in self._producers:
            topic_obj = self.app.topic(topic)
            serializer = lambda v: json.dumps(v).encode("utf-8")
            self._producers[topic] = topic_obj.get_producer(value_serializer=serializer)

        self._producers[topic].produce(value, key=key)

    def flush(self):
        for producer in self._producers.values():
            producer.flush()

kafka_client = KafkaClient()
