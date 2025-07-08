# Knowledge Graph Shared Utils - Architecture Guide

## Overview

This package provides a unified architecture for interacting with both regular PostgreSQL databases and Apache AGE graph databases. The design separates concerns between different types of database operations while maintaining consistency and type safety.

## Database Clients

### DBClient (Regular PostgreSQL Operations)
- **Purpose**: Standard relational database operations using SQLModel
- **Connection Type**: SQLModel `Session`
- **Usage**: CRUD operations on tables, joins, aggregations
- **Location**: `shared_utils.clients.db_client`

```python
from shared_utils.clients.db_client import create_db_client
from shared_utils.queries import documents

db_client = create_db_client()
with db_client.scoped_session() as session:
    doc = documents.get_document(session, document_id)
```

### AGEClient (Apache AGE Graph Operations)
- **Purpose**: Graph database operations using Apache AGE extension
- **Connection Type**: psycopg `Connection`
- **Usage**: Cypher queries, graph traversal, node/edge operations
- **Location**: `shared_utils.clients.age_client`

```python
from shared_utils.clients.age_client import create_age_client
from shared_utils.queries import apache_age

age_client = create_age_client()
with age_client.scoped_session() as conn:
    graph_name = age_client.get_graph_name()
    nodes = apache_age.find_nodes(conn, graph_name, "Person")
```

## Query Modules

### Regular Database Queries
Use SQLModel `Session` objects:
- `documents.py` - Document metadata operations
- `chunks.py` - Document chunk operations  
- `graphs.py` - Graph metadata operations
- `layouts.py` - Layout operations
- `ingestion_jobs.py` - Job tracking operations

### Graph Database Queries
Use psycopg `Connection` objects:
- `apache_age.py` - AGE-specific graph operations

## SQL Models

All SQL models are located in `shared_utils.sql_models/` and use SQLModel:
- `DocumentMetadata` - Document metadata table
- `Chunk` - Document chunks table
- `Graph` - Graph metadata table
- `Layout` - Layout information table
- `IngestionJob` - Job tracking table

### Key Features:
- Consistent UUID primary keys
- Proper foreign key relationships
- Automatic timestamp handling
- Schema-qualified table names

## Connection Management

### Scoped Sessions (Recommended)
Both clients provide scoped session context managers that handle:
- Automatic connection creation
- Transaction management (commit/rollback)
- Resource cleanup

```python
# Regular database
with db_client.scoped_session() as session:
    # Operations here
    pass  # Auto-commit and close

# AGE database  
with age_client.scoped_session() as conn:
    # Operations here
    pass  # Auto-commit and close
```

### Persistent Sessions
For long-running operations, both clients provide persistent sessions:

```python
# Caller responsible for lifecycle
session = db_client.get_persistent_session()
try:
    # Operations
    session.commit()
finally:
    session.close()
```

## Convenience Methods

### AGEClient Convenience Methods
- `get_graph_name()` - Returns configured graph name
- `execute_with_graph(func, *args, **kwargs)` - Executes function with connection and graph name

```python
# Instead of:
with age_client.scoped_session() as conn:
    graph_name = age_client.get_graph_name()
    result = apache_age.find_nodes(conn, graph_name, "Person")

# Use:
result = age_client.execute_with_graph(apache_age.find_nodes, "Person")
```

## Environment Variables

### DBClient (PostgreSQL)
- `POSTGRES_USER` - Database username
- `POSTGRES_PASSWORD` - Database password  
- `POSTGRES_HOST` - Database host (default: localhost)
- `POSTGRES_PORT` - Database port (default: 5432)
- `POSTGRES_DB` - Database name

### AGEClient (Apache AGE)
- `AGE_USER` - Database username
- `AGE_PASSWORD` - Database password
- `AGE_HOST` - Database host (default: localhost)  
- `AGE_PORT` - Database port (default: 5432)
- `AGE_DB` - Database name
- `AGE_GRAPH` - Graph name (default: knowledge_graph)

## Best Practices

1. **Use scoped sessions** whenever possible for automatic resource management
2. **Separate concerns** - use DBClient for relational operations, AGEClient for graph operations
3. **Handle exceptions** appropriately in persistent sessions
4. **Use the convenience methods** for cleaner code
5. **Import from the factory functions** (`create_db_client()`, `create_age_client()`) for singleton behavior

## Migration Notes

If upgrading from previous versions:
- AGE query functions now use `Connection` instead of `Session`
- All query functions now use `UUID` types directly instead of string conversion
- SQL models have been updated with proper foreign key relationships
- Import paths may have changed for some utility functions

## SQL Schema Dependencies

When creating tables, follow this order to respect foreign key dependencies:
1. `DocumentMetadata` (no dependencies)
2. `Graph` (no dependencies)  
3. `Layout` (no dependencies)
4. `IngestionJob` (references DocumentMetadata)
5. `Chunk` (references DocumentMetadata)
