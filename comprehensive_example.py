"""
Complete example showing how to use both DBClient and AGEClient together.

This demonstrates the proper separation of concerns:
- DBClient + SQLModel Session for regular database operations
- AGEClient + psycopg Connection for AGE-specific graph operations
"""

from uuid import uuid4
from shared_utils.clients import db_client
from shared_utils.clients import age_client
from shared_utils.sql_models import DocumentMetadata
from shared_utils.queries import documents, apache_age


def comprehensive_example():
    """Example showing both regular database and AGE graph operations."""
    
    # Regular database operations using SQLModel Session
    print("=== Regular Database Operations ===")
    with db_client.scoped_session() as session:
        # Create a document metadata entry
        doc_id = uuid4()
        doc_metadata = DocumentMetadata(
            id=doc_id,
            filename="example.pdf",
            file_path="/path/to/example.pdf",
            file_size=1024,
            mime_type="application/pdf",
            upload_timestamp=None  # Will be set automatically
        )
        
        # Insert the document
        documents.insert_document(session, doc_metadata)
        print(f"Inserted document: {doc_id}")
        
        # Retrieve the document
        retrieved_doc = documents.get_document(session, doc_id)
        print(f"Retrieved document: {retrieved_doc.filename if retrieved_doc else 'Not found'}")
    
    # AGE graph operations using psycopg Connection
    print("\n=== AGE Graph Operations ===")
    with age_client.scoped_session() as conn:
        graph_name = age_client.get_graph_name()
        
        # Create the graph
        apache_age.create_graph(conn, graph_name)
        print(f"Created/ensured graph: {graph_name}")
        
        # Create a document node in the graph
        doc_props = {
            "document_id": str(doc_id),
            "filename": "example.pdf",
            "type": "document"
        }
        doc_node = apache_age.create_node(conn, graph_name, "Document", doc_props)
        print(f"Created document node: {doc_node}")
        
        # Create an entity node
        entity_props = {
            "name": "Important Entity",
            "type": "entity"
        }
        entity_node = apache_age.create_node(conn, graph_name, "Entity", entity_props)
        print(f"Created entity node: {entity_node}")
        
        # Find all document nodes
        all_docs = apache_age.find_nodes(conn, graph_name, "Document")
        print(f"Found document nodes: {len(all_docs)}")
    
    # Demonstration of convenience method
    print("\n=== Using Convenience Method ===")
    entities = age_client.execute_with_graph(
        apache_age.find_nodes,
        "Entity",
        {"type": "entity"}
    )
    print(f"Found entities using convenience method: {len(entities)}")


if __name__ == "__main__":
    comprehensive_example()
