from typing import cast
from .age_client import AGEClient, create_age_client
from .db_client import DBClient, create_db_client
from .redis_client import RedisClient, create_redis_client
from .s3_client import S3Client, create_s3_client
from .utils.lazy_proxy import LazyProxy

# LazyProxy instances for each client
# This allows the clients to be instantiated only when they are first accessed,
# casting preserves type hints for IDEs and static analysis tools.
age_client:AGEClient = cast(AGEClient,LazyProxy(create_age_client))
db_client:DBClient = cast(DBClient,LazyProxy(create_db_client))
redis_client:RedisClient = cast(RedisClient,LazyProxy(create_redis_client))
s3_client:S3Client = cast(S3Client,LazyProxy(create_s3_client))