from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
from typing import Optional
from uuid import UUID

class Chunk(SQLModel, table=True):
    """
    Represents a chunk of a document.
    """
    chunk_id: UUID = Field(primary_key=True, description="The unique identifier for the chunk.")
    document_id: UUID = Field(foreign_key="documentmetadata.document_id",index=True, description="The source document id.")
    text: str = Field(description="The text content of the chunk.")
    tags: list[dict] = Field(default_factory=list, ssa_column=Column(JSON), description="List of tags associated with the chunk.")
    #TODO: consider making graph_id an index if performance is an issue
    graph_id : Optional[UUID] = Field(default=None, description="The unique identifier for the graph associated with the chunk.")
    status: str = Field(..., description="The processing status of the chunk, e.g., 'pending', 'processed', 'failed'.")