from uuid import UUID
from sqlmodel import SQLModel, Field

class DocumentMetadata(SQLModel):
    """
    Represents a document in the system.
    """
    document_id: UUID = Field(primary_key=True, description="The unique identifier for the document.")
    s3_key : str = Field(..., description="The S3 key where the document is stored.")