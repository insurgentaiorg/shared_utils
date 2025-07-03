from pydantic import BaseModel, Field

class AllChunksProcessedEvent(BaseModel):
    """
    Event triggered when the processing of all chunks associated with a document is finished.
    """
    document_id: str = Field(..., description="The id of the document associated with the processed chunks.")