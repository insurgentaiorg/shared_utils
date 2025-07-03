from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from shared_utils.sql_models.Chunk import Chunk

def get_chunk(session: Session, chunk_id: UUID) -> Optional[Chunk]:
    statement = select(Chunk).where(Chunk.chunk_id == chunk_id)
    result = session.exec(statement).first()
    return result
