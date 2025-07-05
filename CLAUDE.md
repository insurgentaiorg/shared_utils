# InsurgentAI Shared Utils - Tool Index

This shared utilities package (`insurgentai_shared_utils` v0.2.7) provides common functionality for InsurgentAI microservices, particularly for knowledge graph document processing workflows.

## Client Libraries

### Database Client (`shared_utils.db_client`)
- **`db_client`**: Singleton PostgreSQL client using SQLModel/psycopg
- **Environment Variables Required**: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`
- **Methods**:
  - `scoped_session()`: Context manager with auto-commit/rollback/close
  - `get_persistent_session()`: Manual session management

### Redis Streams Client (`shared_utils.redis_streams_client`)
- **`RedisStreamsClient`**: Event streaming with Redis Streams
- **Environment Variables**: `REDIS_URL` (default: redis://localhost:6379/0)
- **Methods**:
  - `send(stream, value)`: Send event to stream
  - `register_callback(stream, group_id, callback)`: Register event handler
  - `stop_consuming(stream)`: Stop consuming from stream

### S3 Client (`shared_utils.s3_client`)
- **`s3_client`**: Singleton AWS S3 client
- **Methods**:
  - `upload_file(local_path, bucket, s3_key)`: Upload file to S3
  - `download_file(bucket, s3_key, local_path)`: Download file from S3

## Data Models

### SQL Models (`shared_utils.sql_models`)
Database entities using SQLModel:
- **`DocumentMetadata`**: Document records with `document_id`, `s3_key`, `status`
- **`Chunk`**: Document chunks with `chunk_id`, `document_id`, `text`, `tags`, `graph_id`, `status`
- **`Graph`**: Knowledge graphs with `graph_id`, `chunk_id`, `entities`, `edges`, `relations`

### Event Contracts (`shared_utils.event_contracts`)
Pydantic models for document processing events:
- **`DocumentUploadedEvent`**: Document upload notification
- **`DocumentChunkingFinishedEvent`**: Chunking completion
- **`ProcessChunkRequestEvent`**: Chunk processing request
- **`AllChunksProcessedEvent`**: All chunks processed
- **`DocumentIngestionFinalizedEvent`**: Ingestion finalization
- **`KnowledgeGraphUpdatedEvent`**: Graph update notification

### API Response Models (`shared_utils.data_models`)
- **`DocumentUploadResponse`**: Upload operation response with `s3_key`

## Query Utilities (`shared_utils.queries`)
Database query functions:
- **`chunks.get_chunk(session, chunk_id)`**: Retrieve chunk by ID
- **`documents.get_document(session, document_id)`**: Retrieve document by ID  
- **`graphs.get_graph(session, graph_id)`**: Retrieve graph by ID

## Serialization Utilities (`shared_utils.serialization_utils`)
- **`deserialize_event`**: Decorator for automatic event deserialization with error handling

## Usage Examples

```python
# Database operations
from shared_utils.db_client import db_client
from shared_utils.sql_models import DocumentMetadata

with db_client.scoped_session() as session:
    doc = DocumentMetadata(document_id=uuid4(), s3_key="docs/file.pdf", status="uploaded")
    session.add(doc)

# Event handling
from shared_utils.redis_streams_client import RedisStreamsClient
from shared_utils.event_contracts import DocumentUploadedEvent

client = RedisStreamsClient()
client.send("document-stream", {"document_id": str(doc_id)})

# S3 operations
from shared_utils.s3_client import s3_client
success = s3_client.upload_file("local.pdf", "my-bucket", "docs/remote.pdf")
```

## Dependencies
- Python >=3.12
- psycopg[binary,pool] >=3.2.6 (PostgreSQL)
- pydantic >=2.11.7 (Data validation)
- sqlmodel >=0.0.24 (SQL ORM)
- redis (Redis Streams)
- boto3==1.39.1 (AWS S3)

## Environment Setup
Required environment variables for full functionality:
```bash
# Database
POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=database_name

# Redis (optional, defaults shown)
REDIS_URL=redis://localhost:6379/0

# AWS credentials configured via boto3 (AWS CLI, IAM roles, etc.)
```