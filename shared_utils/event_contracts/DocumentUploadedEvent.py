from pydantic import BaseModel, Field

class DocumentUploadedEvent(BaseModel):
    """
    Event triggered when a document is uploaded.
    """
    s3_key: str = Field(..., description="The S3 key of the uploaded document.")