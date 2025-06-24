"""
LangGraph implementation for multi-method entity extraction.
This graph orchestrates three different entity extraction methods and aggregates their results.
"""

from typing import Dict, Any
from langchain_core.messages import ToolMessage

from tools import (
    extract_entities_llm,
    extract_entities_spacy,
    extract_entities_gazetteer,
)

from state_and_types import EntityExtractionState, Entities
from utils import load_config
from paths import CONFIG_FILE_PATH
from llm import get_llm

config = load_config(CONFIG_FILE_PATH)

MAX_ENTITIES = config.get("max_entities", 5)


def tools_node(state: EntityExtractionState) -> Dict[str, Any]:
    """Node that executes tool calls."""
    tool_registry = {
        "extract_entities_llm": extract_entities_llm,
        "extract_entities_spacy": extract_entities_spacy,
        "extract_entities_gazetteer": extract_entities_gazetteer,
    }

    last_message = state["messages"][-1]

    tool_messages = []
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        # Execute all tool calls
        for tool_call in last_message.tool_calls:
            result = execute_tool_call(tool_call, tool_registry)
            # Create tool message
            tool_message = ToolMessage(
                content=str(result), tool_call_id=tool_call["id"]
            )
            tool_messages.append(tool_message)

    return {"messages": tool_messages}


def execute_tool_call(tool_call: Dict[str, Any], tool_registry: Dict[str, Any]) -> Any:
    """Execute a single tool call and return the result."""
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]

    if tool_name in tool_registry:
        tool_function = tool_registry[tool_name]
        result = tool_function.invoke(tool_args)
        print(f"🔧 Tool used: {tool_name} with args {tool_args} → Result: {result}")
        return result
    else:
        print(f"Unknown tool: {tool_name}")
        return f"Error: Tool '{tool_name}' not found"


def should_continue(state: EntityExtractionState):
    """Determine whether to continue to tools or end."""
    last_message = state["messages"][-1]

    # If the last message has tool calls, go to tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    # Otherwise, we're done
    return "aggregation"


def llm_extraction_node(state: EntityExtractionState) -> Dict[str, Any]:
    """
    Node that performs LLM-based entity extraction.
    """
    print("🤖 Running LLM-based entity extraction...")
    try:
        entities = extract_entities_llm(
            text=state["text"],
            entity_types=state["entity_types"],
            model_name="gpt-4o-mini",
            parallelize=True,
        )
        print(f"✅ LLM extraction completed: {len(entities)} entities found")
        print("LLM entities:")
        for i, result in enumerate(entities, 1):
            print(f"{i:2d}. {result['name']:25} | {result['type']:15}")
        print("-" * 80)
        return {"llm_entities": entities}
    except Exception as e:
        print(f"❌ LLM extraction failed: {e}")
        return {"llm_entities": []}


def spacy_extraction_node(state: EntityExtractionState) -> Dict[str, Any]:
    """
    Node that performs spaCy-based entity extraction.
    """
    print("🔬 Running spaCy-based entity extraction...")
    try:
        results = extract_entities_spacy(text=state["text"])
        print(f"✅ spaCy extraction completed: {len(results)} entities found")
        print("Spacy results:")
        for i, result in enumerate(results, 1):
            print(f"{i:2d}. {result['name']:25} | {result['type']:15}")
        print("-" * 80)
        return {"spacy_entities": results}
    except Exception as e:
        print(f"❌ spaCy extraction failed: {e}")
        return {"spacy_entities": []}


def gazetteer_extraction_node(state: EntityExtractionState) -> Dict[str, Any]:
    """
    Node that performs predefined dictionary-based entity extraction.
    """
    print("📚 Running Gazetteer entity extraction...")
    try:
        results = extract_entities_gazetteer(text=state["text"])
        print(f"✅ Gazetteer extraction completed: {len(results)} entities found")
        print("Gazetteer results:")
        for i, result in enumerate(results, 1):
            print(f"{i:2d}. {result['name']:25} | {result['type']:15}")
        print("-" * 80)
        return {"gazetteer_entities": results}
    except Exception as e:
        print(f"❌ Gazetteer extraction failed: {e}")
        return {"gazetteer_entities": []}


def aggregation_node(state: EntityExtractionState) -> Dict[str, Any]:
    """
    Node that aggregates entities from all three extraction methods.
    """
    print("🔄 Aggregating entities from all extraction methods...")

    llm = get_llm(config.get("llm", "gpt-4o-mini")).with_structured_output(Entities)
    response = llm.invoke(
        f"""
        Extract the most important entities from the list of entities. 
        Your response should not contain more than {MAX_ENTITIES} entities. 
        Return a list of entities. Keep the format of the entity unchanged.

        Entities:
        {state["llm_entities"]}
        {state["spacy_entities"]}
        {state["gazetteer_entities"]}
        """
    ).model_dump()

    return {"entities": response["entities"]}
