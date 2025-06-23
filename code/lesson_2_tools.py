"""
LangGraph implementation for multi-method entity extraction.
This graph orchestrates three different entity extraction methods and aggregates their results.
"""

import os
from typing import Dict, List, Any, TypedDict, Annotated
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import ToolMessage
from tools import (
    extract_entities_llm,
    extract_entities_spacy,
    extract_entities_predefined,
)

from utils import load_config
from paths import CONFIG_FILE_PATH
from langchain_core.runnables.graph import MermaidDrawMethod
from paths import OUTPUTS_DIR
from llm import get_llm
from tools import Entities

config = load_config(CONFIG_FILE_PATH)


class EntityExtractionState(TypedDict):
    """State class for the entity extraction graph."""

    text: str
    messages: Annotated[List, add_messages]
    entities: List[Dict[str, str]]


def extraction_node(state: EntityExtractionState) -> Dict[str, Any]:
    """
    Node that performs LLM-based entity extraction.
    """
    llm = get_llm(config.get("llm", "gpt-4o-mini")).bind_tools(
        [extract_entities_llm, extract_entities_spacy, extract_entities_predefined]
    )

    # llm = llm.with_structured_output(Entities)

    prompt = f"""
    You are an entity extraction assistant. Follow this workflow:

    1. FIRST: Check if there are any tool results in the conversation history below.
    
    2. IF NO TOOL RESULTS EXIST:
       - Use the available entity extraction tools to analyze the text
       - Call each tool once to get comprehensive results
       - Do not provide a final answer until you have tool results
    
    3. IF TOOL RESULTS ALREADY EXIST:
       - Analyze and summarize the tool results
       - DO NOT call any more tools
       - Provide a final list of the most important entities
    
    Text to analyze: {state["text"]}
    
    Conversation history: {state.get("messages", [])}
    """

    response = llm.invoke(prompt)

    return {"messages": [response]}


def tools_node(state: EntityExtractionState) -> Dict[str, Any]:
    """Node that executes tool calls."""
    tool_registry = {
        "extract_entities_llm": extract_entities_llm,
        "extract_entities_spacy": extract_entities_spacy,
        "extract_entities_predefined": extract_entities_predefined,
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


def aggregation_node(state: EntityExtractionState) -> Dict[str, Any]:
    """Node that aggregates results from all three extraction methods."""
    print("🔄 Aggregating results from all extraction methods...")

    llm = get_llm(config.get("llm", "gpt-4o-mini")).with_structured_output(Entities)

    response = llm.invoke(
        f"""
        Extract the most important entities from the list of entities. 
        Your response should not contain more than 5 entities. 
        Return a list of entities. Keep the format of the entity unchanged.

        Conversation history:
        {state["messages"]}
        """
    ).model_dump()["entities"]

    return {"entities": response}


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


def create_entity_extraction_graph() -> StateGraph:
    """
    Creates and returns the entity extraction graph.
    """
    # Create the graph
    graph = StateGraph(EntityExtractionState)

    graph.add_edge(START, "extraction")
    graph.add_node("extraction", extraction_node)
    graph.add_node("tools", tools_node)
    graph.add_node("aggregation", aggregation_node)
    graph.add_edge("aggregation", END)

    graph.add_conditional_edges(
        "extraction", should_continue, {"tools": "tools", "aggregation": "aggregation"}
    )

    graph.add_edge("tools", "extraction")

    return graph.compile()


def visualize_graph(graph: StateGraph, save_path: str = OUTPUTS_DIR):
    """Visualize the graph."""
    png = graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
    with open(os.path.join(save_path, "agent_with_tools.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    graph = create_entity_extraction_graph()
    visualize_graph(graph)

    sample_text = """
    PyTorch is an amazing framework used to build variational auto-encoders. 
    These models are particularly useful for anomaly detection tasks on datasets like MNIST.
    The transformer architecture has revolutionized natural language processing.
    """

    entities = graph.invoke({"text": sample_text})["entities"]
    print(entities)
