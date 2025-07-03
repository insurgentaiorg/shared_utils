import os
import json
from quixstreams import Application

class KafkaClient:
    def __init__(self):
        self.broker_address = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.client_id = os.getenv("KAFKA_CLIENT_ID", "default-client")
        self._app = None
        self._producers = {}
        self._consumers = {}
        self._callbacks = {}

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

    def register_callback(self, topic: str, group_id: str, callback):
        """
        Register a callback function to be called on each message consumed from `topic`.
        `callback` signature: func(key: bytes|None, value: dict) -> None
        """

        if topic in self._consumers:
            # Already registered consumer for this topic, add callback
            self._callbacks[topic].append(callback)
            return

        topic_obj = self.app.topic(topic)
        consumer = topic_obj.get_consumer(group_id=group_id)
        self._consumers[topic] = consumer
        self._callbacks[topic] = [callback]

        def on_message(msg):
            try:
                val = json.loads(msg.value.decode("utf-8"))
            except Exception:
                val = None
            for cb in self._callbacks[topic]:
                cb(msg.key, val)

        consumer.set_message_callback(on_message)
        consumer.start()

kafka_client = KafkaClient()
