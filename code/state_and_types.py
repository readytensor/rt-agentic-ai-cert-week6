
from typing import Dict, List, TypedDict, Optional
from pydantic import BaseModel, Field

class EntityExtractionState(TypedDict):
    """State class for the entity extraction graph."""
    text: str
    entity_types: List[str]
    llm_entities: List[Dict[str, str]]
    spacy_entities: List[Dict[str, str]]
    gazetteer_entities: List[Dict[str, str]]
    entities: List[Dict[str, str]]


class Entity(BaseModel):
    name: str = Field(description="The entity name")
    type: Optional[str] = Field(
        description="The entity type or 'none of the above' if not confidently classified."
    )
    description: str = Field(
        description="A comprehensive description of the entity and its attributes"
    )


class Entities(BaseModel):
    entities: List[Entity] = Field(
        description="The extracted entities. Can be empty if no entities are found.",
    )