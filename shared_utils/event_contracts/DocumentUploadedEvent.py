from pydantic import BaseModel, Field

class DocumentUploadedEvent(BaseModel):
    """
    Event triggered when a document is uploaded.
    """
    id: str = Field(..., description="The S3 key of the uploaded document.")