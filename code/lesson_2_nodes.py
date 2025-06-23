"""
LangGraph implementation for multi-method entity extraction.
This graph orchestrates three different entity extraction methods and aggregates their results.
"""

import os
from typing import Dict, List, Any, TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from tools import (
    extract_entities_llm,
    extract_entities_spacy,
    extract_entities_predefined,
)

from utils import load_config
from paths import PROMPT_CONFIG_FILE_PATH, CONFIG_FILE_PATH
from langchain_core.runnables.graph import MermaidDrawMethod
from paths import OUTPUTS_DIR
from llm import get_llm
from tools import Entities

config = load_config(CONFIG_FILE_PATH)


class EntityExtractionState(TypedDict):
    """State class for the entity extraction graph."""

    text: str
    entity_types: List[str]
    llm_results: List[Dict[str, str]]
    spacy_results: List[Dict[str, str]]
    predefined_results: List[Dict[str, str]]
    entities: List[Dict[str, str]]


def llm_extraction_node(state: EntityExtractionState) -> Dict[str, Any]:
    """
    Node that performs LLM-based entity extraction.
    """
    print("🤖 Running LLM-based entity extraction...")
    try:
        results = extract_entities_llm.func(
            text=state["text"],
            entity_types=state["entity_types"],
            model_name="gpt-4o-mini",
            parallelize=False,  # Keep it simple for demo
        )
        print(f"✅ LLM extraction completed: {len(results)} entities found")
        print("LLM results:")
        for i, result in enumerate(results):
            print(f"{i:2d}. {result['name']:25} | {result['type']:15}")
        print("-" * 80)
        return {"llm_results": results}
    except Exception as e:
        print(f"❌ LLM extraction failed: {e}")
        return {"llm_results": []}


def spacy_extraction_node(state: EntityExtractionState) -> Dict[str, Any]:
    """
    Node that performs spaCy-based entity extraction.
    """
    print("🔬 Running spaCy-based entity extraction...")
    try:
        results = extract_entities_spacy.func(text=state["text"])
        print(f"✅ spaCy extraction completed: {len(results)} entities found")
        print("Spacy results:")
        for i, result in enumerate(results):
            print(f"{i:2d}. {result['name']:25} | {result['type']:15}")
        print("-" * 80)
        return {"spacy_results": results}
    except Exception as e:
        print(f"❌ spaCy extraction failed: {e}")
        return {"spacy_results": []}


def predefined_extraction_node(state: EntityExtractionState) -> Dict[str, Any]:
    """
    Node that performs predefined dictionary-based entity extraction.
    """
    print("📚 Running predefined entity extraction...")
    try:
        results = extract_entities_predefined.func(text=state["text"])
        print(f"✅ Predefined extraction completed: {len(results)} entities found")
        print("Predefined results:")
        for i, result in enumerate(results):
            print(f"{i:2d}. {result['name']:25} | {result['type']:15}")
        print("-" * 80)
        return {"predefined_results": results}
    except Exception as e:
        print(f"❌ Predefined extraction failed: {e}")
        return {"predefined_results": []}


def aggregation_node(state: EntityExtractionState) -> Dict[str, Any]:
    """
    Node that aggregates results from all three extraction methods.
    """
    print("🔄 Aggregating results from all extraction methods...")

    llm = get_llm(config.get("llm", "gpt-4o-mini")).with_structured_output(Entities)
    response = llm.invoke(
        f"""
        Extract the most important entities from the list of entities. 
        Your response should not contain more than 5 entities. 
        Return a list of entities. Keep the format of the entity unchanged.

        Entities:
        {state["llm_results"]}
        {state["spacy_results"]}
        {state["predefined_results"]}
        """
    ).model_dump()

    return {"entities": response["entities"]}


def create_entity_extraction_graph() -> StateGraph:
    """
    Creates and returns the entity extraction graph.
    """
    # Create the graph
    graph = StateGraph(EntityExtractionState)

    # Add nodes
    graph.add_node("llm_extraction", llm_extraction_node)
    graph.add_node("spacy_extraction", spacy_extraction_node)
    graph.add_node("predefined_extraction", predefined_extraction_node)
    graph.add_node("aggregation", aggregation_node)

    # Add edges
    # Start node connects to all three extraction methods in parallel
    graph.add_edge(START, "llm_extraction")
    graph.add_edge(START, "spacy_extraction")
    graph.add_edge(START, "predefined_extraction")

    # All extraction methods feed into aggregation
    graph.add_edge("llm_extraction", "aggregation")
    graph.add_edge("spacy_extraction", "aggregation")
    graph.add_edge("predefined_extraction", "aggregation")

    # Aggregation leads to end
    graph.add_edge("aggregation", END)

    return graph.compile()


def visualize_graph(graph: StateGraph, save_path: str = OUTPUTS_DIR):
    """Visualize the graph."""
    png = graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
    with open(os.path.join(save_path, "graph.png"), "wb") as f:
        f.write(png)


def run_entity_extraction(
    text: str, entity_types: Optional[List[str]] = None
) -> List[Dict[str, str]]:
    """
    Convenience function to run the entity extraction graph.

    Args:
        text: The text to extract entities from
        entity_types: List of entity types to extract (defaults to common types)

    Returns:
        List of extracted entities with their methods and types
    """
    if entity_types is None:
        entity_types = ["algorithm", "dataset", "tool", "framework", "model", "task"]

    # Load configuration
    config = load_config(PROMPT_CONFIG_FILE_PATH)

    # Create initial state
    initial_state = EntityExtractionState(
        text=text,
        entity_types=entity_types,
        llm_results=[],
        spacy_results=[],
        predefined_results=[],
        entities=[],
    )

    # Create and run the graph
    graph = create_entity_extraction_graph()
    visualize_graph(graph)
    final_state = graph.invoke(initial_state)

    return final_state["entities"]


if __name__ == "__main__":
    # Example usage
    sample_text = """
    PyTorch is an amazing framework used to build variational auto-encoders. 
    These models are particularly useful for anomaly detection tasks on datasets like MNIST.
    The transformer architecture has revolutionized natural language processing.
    """

    print("=" * 80)
    print("🔍 MULTI-METHOD ENTITY EXTRACTION DEMO")
    print("=" * 80)

    results = run_entity_extraction(
        text=sample_text,
        entity_types=["algorithm", "dataset", "tool", "framework", "model", "task"],
    )

    print("\n" + "=" * 80)
    print("🎯 FINAL AGGREGATED RESULTS")
    print("=" * 80)

    for i, entity in enumerate(results, 1):
        print(f"{i:2d}. {entity['name']:25} | {entity['type']:15}")

    print(f"\nTotal unique entities extracted: {len(results)}")
