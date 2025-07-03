import os
import json
from quixstreams import QuixKafkaConsumer, QuixKafkaProducer, QuixKafkaConfiguration

class KafkaClient:
    def __init__(self):
        self.config = QuixKafkaConfiguration(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            security_protocol="PLAINTEXT",
            client_id=os.getenv("KAFKA_CLIENT_ID", "default-client")
        )
        self._producer = None

    @property
    def producer(self):
        if self._producer is None:
            self._producer = QuixKafkaProducer(self.config)
        return self._producer

    def send(self, topic: str, value: dict, key: str | None = None):
        self.producer.publish(
            topic,
            key=key,
            value=json.dumps(value),
            content_type="application/json"
        )

    def create_consumer(self, topic: str, group_id: str) -> QuixKafkaConsumer:
        return QuixKafkaConsumer(
            topics=[topic],
            group_id=group_id,
            auto_offset_reset="earliest",
            config=self.config,
            value_deserializer=lambda m: json.loads(m)
        )

kafka_client = KafkaClient() # module level singleton instance
