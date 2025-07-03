from pydantic import BaseModel

class KnowledgeGraphUpdatedEvent(BaseModel):
    """
    Event triggered when the knowledge graph is updated.
    """