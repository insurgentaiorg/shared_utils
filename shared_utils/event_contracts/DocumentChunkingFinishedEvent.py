from pydantic import BaseModel, Field

class DocumentChunkingFinishedEvent(BaseModel):
    """
    Event triggered when the chunking of a document is finished.
    """
    id: str = Field(..., description="The document ID associated with the chunking process.")