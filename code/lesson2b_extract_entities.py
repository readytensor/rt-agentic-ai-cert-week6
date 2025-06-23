from langgraph.graph import StateGraph, START, END
from langchain_core.runnables.graph import MermaidDrawMethod
from typing import Dict, List, Optional
import os

from nodes import(
    llm_extraction_node,
    spacy_extraction_node,
    gazetteer_extraction_node,
    aggregation_node,
)
from paths import OUTPUTS_DIR, CONFIG_FILE_PATH
from state_and_types import EntityExtractionState
from paths import OUTPUTS_DIR
from utils import load_publication_example, load_config

config = load_config(CONFIG_FILE_PATH)

def create_entity_extraction_graph() -> StateGraph:
    """
    Creates and returns the entity extraction graph.
    """
    # Create the graph
    graph = StateGraph(EntityExtractionState)

    # Add nodes
    graph.add_node("llm_extraction", llm_extraction_node)
    graph.add_node("spacy_extraction", spacy_extraction_node)
    graph.add_node("gazetteer_extraction", gazetteer_extraction_node)
    graph.add_node("aggregation", aggregation_node)

    # Add edges
    # Start node connects to all three extraction methods in parallel
    graph.add_edge(START, "llm_extraction")
    graph.add_edge(START, "spacy_extraction")
    graph.add_edge(START, "gazetteer_extraction")

    # All extraction methods feed into aggregation
    graph.add_edge("llm_extraction", "aggregation")
    graph.add_edge("spacy_extraction", "aggregation")
    graph.add_edge("gazetteer_extraction", "aggregation")

    # Aggregation leads to end
    graph.add_edge("aggregation", END)

    return graph.compile()


def visualize_graph(graph: StateGraph, save_path: str = OUTPUTS_DIR):
    """Visualize the graph."""
    print("Visualizing the entity extraction graph...")
    print(graph.get_graph().draw_mermaid())
    # Save the graph as PNG
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

    # Create initial state
    initial_state = EntityExtractionState(
        text=text,
        entity_types=entity_types,
        llm_results=[],
        spacy_results=[],
        gazetteer_results=[],
        entities=[],
    )

    # Create and run the graph
    graph = create_entity_extraction_graph()
    visualize_graph(graph)
    final_state = graph.invoke(initial_state)

    return final_state["entities"]


if __name__ == "__main__":

    # ⚠️⚠️⚠️ CAUTION: LONG + EXPENSIVE INPUTS ⚠️⚠️⚠️
    # -------------------------------------------------------------------------------
    # 🚨 Publication examples 2 and 3 are large and may take several minutes to process.
    # 💸 They will consume a lot of tokens — which could cost you a few cents.
    #
    # 👉 For faster and cheaper runs:
    #    - Use example 1
    #    - Or create shorter versions of examples 2 and 3
    #
    # ✅ This project is for learning — don’t burn through tokens unnecessarily.
    # -------------------------------------------------------------------------------

     # Example usage
    sample_text = load_publication_example(1) # ⚠️ CAUTION: SEE NOTE ABOVE

    print("=" * 80)
    print("🔍 MULTI-METHOD ENTITY EXTRACTION DEMO")
    print("=" * 80)

    results = run_entity_extraction(
        text=sample_text,
        entity_types=config["entity_types"],
    )

    print("\n" + "=" * 80)
    print("🎯 FINAL EXTRACTED ENTITIES")
    print("=" * 80)

    for i, entity in enumerate(results, 1):
        print(f"{i:2d}. {entity['name']:25} | {entity['type']:15}")

    print(f"\nTotal unique entities extracted: {len(results)}")
