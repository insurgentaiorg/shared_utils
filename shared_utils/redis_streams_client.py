import os
import json
import redis
import threading

class RedisStreamsClient:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client = redis.from_url(redis_url)
        self._consumers = {}
        self._callbacks = {}
        self._stop_flags = {}

    def send(self, stream: str, value: dict):
        # Serialize entire dict as single JSON string under 'data' field
        message = {"data": json.dumps(value)}
        self._client.xadd(stream, message)

    def flush(self):
        # No flush needed for Redis Streams
        pass

    def register_callback(self, stream: str, group_id: str, callback):
        if stream in self._consumers:
            self._callbacks[stream].append(callback)
            return

        try:
            self._client.xgroup_create(stream, group_id, id='0', mkstream=True)
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise

        self._callbacks[stream] = [callback]
        self._stop_flags[stream] = False

        def consume_loop():
            consumer_name = f"{group_id}-consumer"
            while not self._stop_flags[stream]:
                resp = self._client.xreadgroup(
                    groupname=group_id,
                    consumername=consumer_name,
                    streams={stream: '>'},
                    count=10,
                    block=1000
                )
                if not resp:
                    continue
                for _, messages in resp:
                    for msg_id, fields in messages:
                        data_json = fields.get(b'data') or fields.get('data')
                        if data_json:
                            try:
                                val = json.loads(data_json)
                            except Exception:
                                val = None
                        else:
                            val = None
                        for cb in self._callbacks[stream]:
                            cb(msg_id, val)
                        self._client.xack(stream, group_id, msg_id)

        t = threading.Thread(target=consume_loop, daemon=True)
        t.start()
        self._consumers[stream] = t

    def stop_consumer(self, stream: str):
        if stream in self._stop_flags:
            self._stop_flags[stream] = True
            self._consumers[stream].join()
            del self._consumers[stream]
            del self._callbacks[stream]
            del self._stop_flags[stream]

redis_streams_client = RedisStreamsClient()
