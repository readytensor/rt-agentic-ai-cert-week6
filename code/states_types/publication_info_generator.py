from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field


class ContentProcessingState(TypedDict):
    """State class for the content processing graph."""

    text: str
    tldr: Optional[str]
    title: Optional[str]
    tags: Optional[List[str]]
    references: Optional[List[str]]
    manager_decision: Optional[str]
    revision_round: Optional[int]
    needs_revision: Optional[bool]
    # Individual feedback for each level 2 node
    tldr_feedback: Optional[str]
    title_feedback: Optional[str]
    references_feedback: Optional[str]
    # Individual approval status for each component
    tldr_approved: Optional[bool]
    title_approved: Optional[bool]
    references_approved: Optional[bool]


class SearchQueries(BaseModel):
    queries: List[str] = Field(
        description="The search queries to find relevant references"
    )


class Reference(BaseModel):
    url: str = Field(description="The URL of the reference")
    title: str = Field(description="The title of the reference")


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
