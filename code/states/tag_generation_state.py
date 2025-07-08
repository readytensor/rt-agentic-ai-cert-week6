from typing import Dict, List, TypedDict
from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.messages import HumanMessage, SystemMessage
from typing_extensions import Annotated

from prompt_builder import build_system_prompt_message


class TagGenerationState(TypedDict):
    """State class for the tag extraction graph."""

    input_text: str

    llm_tags_gen_messages: Annotated[list[AnyMessage], add_messages]
    tag_type_assigner_messages: Annotated[list[AnyMessage], add_messages]
    tags_selector_messages: Annotated[list[AnyMessage], add_messages]

    llm_tags: List[Dict[str, str]]
    spacy_tags: List[Dict[str, str]]
    gazetteer_tags: List[Dict[str, str]]
    candidate_tags: List[Dict[str, str]]
    selected_tags: List[Dict[str, str]]
    max_tags: int


def generate_tag_types_prompt(tag_types: List[Dict[str, str]]) -> str:
    """
    Generates a readable string version of tag types and their descriptions for LLM input.

    Args:
        tag_types: A list of dictionaries, each with 'name' and 'description' keys.

    Returns:
        A formatted string listing tag types with descriptions, suitable for use in prompts.
    """
    if not tag_types:
        return "No tag types provided."

    lines = []
    for tag in tag_types:
        name = tag.get("name", "").strip()
        description = tag.get("description", "").strip()
        if name and description:
            lines.append(f"- **{name}**: {description}")
    return "\n".join(lines)


def initialize_tag_generation_state(
    input_text: str,
    llm_tags_generator_prompt_cfg: dict,
    tag_type_assigner_prompt_cfg: dict,
    tags_selector_prompt_cfg: dict,
    tag_types: List[Dict[str, str]],
    max_tags: int = 10,
) -> TagGenerationState:
    """Initializes the state for the tag generation graph."""
    tag_types_prompt = generate_tag_types_prompt(tag_types)
    llm_tags_gen_messages = [
        SystemMessage(build_system_prompt_message(llm_tags_generator_prompt_cfg)),
        SystemMessage(f"Here are the tag types you can assign:\n\n{tag_types_prompt}"),
        HumanMessage(f"Here's your input text for tags generation:\n\n{input_text}"),
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
    return TagGenerationState(
        input_text=input_text,
        llm_tags_gen_messages=llm_tags_gen_messages,
        tag_type_assigner_messages=tag_type_assigner_messages,
        tags_selector_messages=tags_selector_messages,
        llm_tags=[],
        spacy_tags=[],
        gazetteer_tags=[],
        all_tags=[],
        selected_tags=[],
    )
