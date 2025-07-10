from typing import List, Optional
from pydantic import BaseModel, Field


class Entity(BaseModel):
    name: str = Field(description="The entity name")
    type: Optional[str] = Field(
        description="The entity type or 'Other' if not confidently classified."
    )


class Entities(BaseModel):
    entities: List[Entity] = Field(
        description="The extracted entities. Can be empty if no entities are found.",
    )


class SearchQueries(BaseModel):
    queries: List[str] = Field(
        description="The search queries to find relevant references"
    )


class Reference(BaseModel):
    url: str = Field(description="The URL of the reference")
    title: str = Field(description="The title of the reference")
    page_content: str = Field(description="The content of the reference page")


class References(BaseModel):
    references: List[Reference] = Field(description="List of references.")


class ReviewOutput(BaseModel):
    # Individual component approval and feedback
    tldr_approved: bool = Field(description="Whether the TLDR summary is approved")
    tldr_feedback: str = Field(description="Specific feedback for the TLDR summary")
    title_approved: bool = Field(description="Whether the title is approved")
    title_feedback: str = Field(description="Specific feedback for the title")
    references_approved: bool = Field(description="Whether the references are approved")
    references_feedback: str = Field(description="Specific feedback for the references")
