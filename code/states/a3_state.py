from typing import List, Optional, TypedDict, Sequence, Dict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph.message import AnyMessage, add_messages
from pprint import pprint
from typing_extensions import Annotated


from prompt_builder import build_system_prompt_message
from states.tag_generation_state import TagGenerationState, generate_tag_types_prompt


class A3SystemState(TypedDict, TagGenerationState):
    """State class for the A3 system."""

    input_text: str

    manager_messages: Annotated[list[AnyMessage], add_messages]
    manager_brief: Optional[str]

    title_gen_messages: Annotated[list[AnyMessage], add_messages]
    tldr_gen_messages: Annotated[list[AnyMessage], add_messages]
    references_gen_messages: Annotated[list[AnyMessage], add_messages]
    references_selector_messages: Annotated[list[AnyMessage], add_messages]
    reviewer_messages: Annotated[list[AnyMessage], add_messages]

    tldr: Optional[str]
    title: Optional[str]
    reference_search_queries: Optional[str]
    candidate_references: Optional[List[Dict[str, str]]]
    selected_references: Optional[List[str]]

    # Revision information
    revision_round: Optional[int]
    needs_revision: Optional[bool]
    tldr_feedback: Optional[str]
    title_feedback: Optional[str]
    references_feedback: Optional[str]
    # Individual approval status for each component
    tldr_approved: Optional[bool]
    title_approved: Optional[bool]
    references_approved: Optional[bool]
    max_revisions: Optional[int]
    max_search_queries: Optional[int]
    max_references: Optional[int]


def initialize_a3_state(
    input_text: str,
    manager_prompt_cfg: dict,
    llm_tags_generator_prompt_cfg: dict,
    tag_type_assigner_prompt_cfg: dict,
    tags_selector_prompt_cfg: dict,
    max_tags: int,
    tag_types: List[Dict[str, str]],
    title_gen_prompt_cfg: dict,
    tldr_gen_prompt_cfg: dict,
    references_gen_prompt_cfg: dict,
    max_search_queries: int,
    references_selector_prompt_cfg: dict,
    max_references: int,
    reviewer_prompt_cfg: dict,
    max_revisions: int,
) -> A3SystemState:
    """Initialize the A3 system state with default values."""
    # manager system prompt
    manager_messages = [
        SystemMessage(build_system_prompt_message(manager_prompt_cfg)),
        HumanMessage(f"Here's your input text:\n\n{input_text}"),
    ]

    title_gen_messages = [
        SystemMessage(build_system_prompt_message(title_gen_prompt_cfg)),
        SystemMessage(f"Here's your input text for title generation:\n\n{input_text}"),
    ]
    tldr_gen_messages = [
        SystemMessage(build_system_prompt_message(tldr_gen_prompt_cfg)),
        SystemMessage(f"Here's your input text for TL;DR generation:\n\n{input_text}"),
    ]
    # worker nodes system prompts. we dont add the publication text yet
    tag_types_prompt = generate_tag_types_prompt(tag_types)
    llm_tags_gen_messages = [
        SystemMessage(build_system_prompt_message(llm_tags_generator_prompt_cfg)),
        SystemMessage(f"Here are the tag types you can assign:\n\n{tag_types_prompt}"),
        SystemMessage(f"Here's your input text for tags generation:\n\n{input_text}"),
    ]
    tag_type_assigner_messages = [
        SystemMessage(build_system_prompt_message(tag_type_assigner_prompt_cfg)),
        SystemMessage(f"Here are the tag types you can assign:\n\n{tag_types_prompt}"),
        SystemMessage(
            f"Here's your input text for tag type assignment:\n\n{input_text}"
        ),
    ]
    tags_selector_messages = [
        SystemMessage(build_system_prompt_message(tags_selector_prompt_cfg)),
        SystemMessage(
            f"Here's your input text for tag selection reference:\n\n{input_text}"
        ),
        SystemMessage(
            f"Please select at most {max_tags} tags from the generated list."
        ),
    ]
    references_gen_messages = [
        SystemMessage(build_system_prompt_message(references_gen_prompt_cfg)),
        SystemMessage(
            f"Here's your input text for generating search queries:\n\n{input_text}"
        ),
        SystemMessage(
            f"Please generate at most {max_search_queries} search queries from the generated list."
        ),
    ]
    references_selector_messages = [
        SystemMessage(build_system_prompt_message(references_selector_prompt_cfg)),
        SystemMessage(
            f"Here's your input text for selecting appropriate references:\n\n{input_text}"
        ),
        SystemMessage(
            f"Please select at most {max_references} references from the given list of references."
        ),
    ]
    reviewer_messages = [
        SystemMessage(build_system_prompt_message(reviewer_prompt_cfg)),
        SystemMessage(f"Here's your input text for review work:\n\n{input_text}"),
    ]

    return A3SystemState(
        input_text=input_text,
        manager_brief=None,
        manager_messages=manager_messages,
        title_gen_messages=title_gen_messages,
        llm_tags_gen_messages=llm_tags_gen_messages,
        tag_type_assigner_messages=tag_type_assigner_messages,
        tags_selector_messages=tags_selector_messages,
        tldr_gen_messages=tldr_gen_messages,
        references_gen_messages=references_gen_messages,
        references_selector_messages=references_selector_messages,
        reviewer_messages=reviewer_messages,
        tldr=None,
        title=None,
        llm_tags=[],
        spacy_tags=[],
        gazetteer_tags=[],
        all_tags=[],
        selected_tags=[],
        reference_search_queries=None,
        candidate_references=[],
        selected_references=[],
        revision_round=0,
        needs_revision=False,
        tldr_feedback=None,
        title_feedback=None,
        references_feedback=None,
        tldr_approved=False,
        title_approved=False,
        references_approved=False,
        max_revisions=max_revisions,
        max_tags=max_tags,
        tag_types=tag_types,
    )
