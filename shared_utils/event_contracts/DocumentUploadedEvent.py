from pydantic import BaseModel, Field

class DocumentUploadedEvent(BaseModel):
    """
    Event triggered when a document is uploaded.
    """
    document_id: str = Field(..., description="The S3 key of the uploaded document.")