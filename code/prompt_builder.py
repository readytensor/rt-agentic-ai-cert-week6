"""
Prompt template construction functions for building modular prompts.
"""

from typing import Union, List, Optional, Dict, Any
from utils import load_config
from paths import REASONING_CONFIG_FILE_PATH


def lowercase_first_char(text: str) -> str:
    """Lowercases the first character of a string.

    Args:
        text: Input string.

    Returns:
        The input string with the first character lowercased.
    """
    return text[0].lower() + text[1:] if text else text


def format_prompt_section(lead_in: str, value: Union[str, List[str]]) -> str:
    """Formats a prompt section by joining a lead-in with content.

    Args:
        lead_in: Introduction sentence for the section.
        value: Section content, as a string or list of strings.

    Returns:
        A formatted string with the lead-in followed by the content.
    """
    if isinstance(value, list):
        formatted_value = "\n".join(f"- {item}" for item in value)
    else:
        formatted_value = value
    return f"{lead_in}\n{formatted_value}"


reasoning_strategies = load_config(REASONING_CONFIG_FILE_PATH).get(
    "reasoning_strategies", {}
)


def build_prompt_body(
    prompt_config: Dict[str, Any],
    input_data: str = "",
    finalize: bool = True,  # <-- new flag
) -> str:
    """Constructs the full prompt body from a modular prompt config.

    This function assembles a structured prompt using the components defined in the
    provided `config`. It supports optional reasoning strategies, examples, constraints,
    and formatting instructions. It is used as a common base for both one-shot prompt
    strings and chat-based system messages.

    Args:
        config (Dict[str, Any]): Dictionary containing modular prompt components such as
            `role`, `instruction`, `context`, `output_constraints`, `style_or_tone`,
            `output_format`, `examples`, `goal`, and `reasoning_strategy`.
        input_data (str, optional): The user-provided content to be embedded into the prompt,
            typically the document or text to be processed. Defaults to an empty string.
        app_config (Optional[Dict[str, Any]]): Optional application-wide config, typically used
            to look up reasoning strategy templates by name. Defaults to None.
        finalize (bool, optional): Whether to append the final instruction
            ("Now perform the task as instructed above.") to the prompt. This should be True
            for one-shot prompts, and False for chat-based system prompts. Defaults to True.

    Returns:
        str: A fully assembled prompt body string suitable for use in either one-shot or chat contexts.

    Raises:
        ValueError: If the required `instruction` field is missing from the config.
    """
    prompt_parts = []

    if role := prompt_config.get("role"):
        prompt_parts.append(f"You are {lowercase_first_char(role.strip())}.")

    instruction = prompt_config.get("instruction")
    if not instruction:
        raise ValueError("Missing required field: 'instruction'")
    prompt_parts.append(format_prompt_section("Your task is as follows:", instruction))

    if context := prompt_config.get("context"):
        prompt_parts.append(f"Here’s some background that may help you:\n{context}")

    if constraints := prompt_config.get("output_constraints"):
        prompt_parts.append(
            format_prompt_section(
                "Ensure your response follows these rules:", constraints
            )
        )

    if tone := prompt_config.get("style_or_tone"):
        prompt_parts.append(
            format_prompt_section(
                "Follow these style and tone guidelines in your response:", tone
            )
        )

    if format_ := prompt_config.get("output_format"):
        prompt_parts.append(
            format_prompt_section("Structure your response as follows:", format_)
        )

    if examples := prompt_config.get("examples"):
        prompt_parts.append("Here are some examples to guide your response:")
        if isinstance(examples, list):
            for i, example in enumerate(examples, 1):
                prompt_parts.append(f"Example {i}:\n{example}")
        else:
            prompt_parts.append(str(examples))

    if goal := prompt_config.get("goal"):
        prompt_parts.append(f"Your goal is to achieve the following outcome:\n{goal}")

    if input_data:
        prompt_parts.append(
            "Here is the content you need to work with:\n"
            "<<<BEGIN CONTENT>>>\n"
            "```\n" + input_data.strip() + "\n```\n<<<END CONTENT>>>"
        )

    if reasoning := prompt_config.get("reasoning_strategy"):
        strategy_prompt = reasoning_strategies.get(reasoning, "")
        if strategy_prompt:
            prompt_parts.append(strategy_prompt.strip())

    if finalize:
        prompt_parts.append("Now perform the task as instructed above.")
    return "\n\n".join(prompt_parts)


def build_one_shot_prompt(
    prompt_config: Dict[str, Any],
    input_data: str = "",
) -> str:
    """Returns a single prompt string, suitable for one-shot use."""
    return build_prompt_body(prompt_config, input_data, finalize=True)


def build_system_prompt_message(
    config: Dict[str, Any],
) -> str:
    """Returns a system message dict for message-based LLM interfaces."""
    return build_prompt_body(config, input_data="", finalize=False)


def print_prompt_preview(prompt: str, max_length: int = 500) -> None:
    """Prints a preview of the constructed prompt for debugging purposes.

    Args:
        prompt: The constructed prompt string.
        max_length: Maximum number of characters to show.
    """
    print("=" * 60)
    print("CONSTRUCTED PROMPT:")
    print("=" * 60)
    if len(prompt) > max_length:
        print(prompt[:max_length] + "...")
        print(f"\n[Truncated - Full prompt is {len(prompt)} characters]")
    else:
        print(prompt)
    print("=" * 60)
