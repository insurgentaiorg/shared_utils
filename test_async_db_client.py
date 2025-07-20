import asyncio
import os
import uuid
from sqlalchemy import select, text

# Set database environment variables for testing
# Replace these with your actual database credentials
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_PASSWORD"] = "password"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_DB"] = "kg_db"

# Import after setting environment variables
from shared_utils.clients.async_db_client import async_db_client

async def test_connection():
    """Test the database connection."""
    print("Testing async database connection...")
    
    async with async_db_client.scoped_session() as session:
        # Simple query to test connection
        result = await session.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"PostgreSQL version: {version}")

async def test_with_models():
    """Test operations with SQL models.
    
    Uncomment and adapt this function based on your actual models.
    """
    # from shared_utils.sql_models import DocumentMetadata
    
    # async with async_db_client.scoped_session() as session:
    #     # Query example
    #     stmt = select(DocumentMetadata).limit(5)
    #     result = await session.execute(stmt)
    #     docs = result.scalars().all()
    #     
    #     print(f"Found {len(docs)} documents")
    #     for doc in docs:
    #         print(f"Document {doc.document_id}: {doc.s3_key} - Status: {doc.status}")
    #     
    #     # Create example
    #     new_doc = DocumentMetadata(
    #         document_id=str(uuid.uuid4()),
    #         s3_key=f"test/doc-{uuid.uuid4()}.pdf",
    #         status="test"
    #     )
    #     session.add(new_doc)
    #     await session.commit()
    #     print(f"Created new document with ID: {new_doc.document_id}")
    
    pass

async def test_get_persistent_session():
    """Test using a persistent session."""
    session = await async_db_client.get_persistent_session()
    
    try:
        # Run a simple query
        result = await session.execute(text("SELECT current_timestamp"))
        timestamp = result.scalar()
        print(f"Current timestamp: {timestamp}")
        
        # Commit changes
        await session.commit()
    except Exception as e:
        # Rollback on error
        await session.rollback()
        print(f"Error: {e}")
    finally:
        # Always close the session
        await session.close()

async def main():
    """Run all tests."""
    await test_connection()
    # await test_with_models()  # Uncomment when ready to test with actual models
    await test_get_persistent_session()

if __name__ == "__main__":
    asyncio.run(main())