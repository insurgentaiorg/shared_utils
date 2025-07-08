# Knowledge Graph Shared Utils

Shared utilities for the Knowledge Graph system, providing database clients, SQL models, and query utilities for both regular PostgreSQL operations and Apache AGE graph database operations.

## Features

- **Dual Database Support**: Separate clients for PostgreSQL (SQLModel) and Apache AGE (psycopg)
- **Type-Safe Models**: SQLModel-based SQL models with proper relationships
- **Query Utilities**: Modular query functions for different data types
- **Connection Management**: Scoped and persistent session support
- **Event Contracts**: Standardized event definitions for system communication

## Quick Start

```python
from shared_utils.clients.db_client import create_db_client
from shared_utils.clients.age_client import create_age_client
from shared_utils.queries import documents, apache_age

# Regular database operations
db_client = create_db_client()
with db_client.scoped_session() as session:
    doc = documents.get_document(session, document_id)

# Graph database operations  
age_client = create_age_client()
with age_client.scoped_session() as conn:
    nodes = apache_age.find_nodes(conn, age_client.get_graph_name(), "Person")
```

## Documentation

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed documentation on:
- Database client architecture
- SQL models and relationships
- Query module organization
- Environment configuration
- Best practices and migration notes

## Installation

Install with your package manager:
```bash
pip install -e .
```

Required dependencies are specified in `pyproject.toml`.

## Environment Variables

See the architecture guide for complete environment variable requirements for both PostgreSQL and Apache AGE connections.