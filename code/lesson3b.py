"""
LangGraph implementation for multi-stage content processing.
This graph orchestrates content analysis through multiple specialized nodes
managed by a coordinator and reviewed by a final reviewer.
"""

import os
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables.graph import MermaidDrawMethod
from utils import load_config
from paths import CONFIG_FILE_PATH, OUTPUTS_DIR
from states_types.publication_info_generator import ContentProcessingState
from nodes.publication_info_generator_nodes import (
    manager_node,
    tldr_generator_node,
    title_generator_node,
    tags_extractor_node,
    web_search_references_generator_node,
    revision_dispatcher_node,
    reviewer_node,
    route_from_reviewer,
)

config = load_config(CONFIG_FILE_PATH)


def create_content_processing_graph() -> StateGraph:
    """
    Creates and returns the content processing graph with hierarchical structure and feedback loop.
    """
    # Create the graph
    graph = StateGraph(ContentProcessingState)

    # Add nodes
    # Level 1: Manager
    graph.add_node("manager", manager_node)

    # Level 2: Processing nodes
    graph.add_node("tldr_generator", tldr_generator_node)
    graph.add_node("title_generator", title_generator_node)
    graph.add_node("tags_extractor", tags_extractor_node)
    graph.add_node(
        "web_search_references_generator",
        web_search_references_generator_node,
    )

    # Level 2.5: Revision dispatcher (handles parallel revision coordination)
    graph.add_node("revision_dispatcher", revision_dispatcher_node)

    # Level 3: Reviewer
    graph.add_node("reviewer", reviewer_node)

    # Add edges - hierarchical structure with feedback loop
    # START -> Manager (Level 1)
    graph.add_edge(START, "manager")

    # Manager -> All Level 2 nodes (parallel processing)
    graph.add_edge("manager", "tldr_generator")
    graph.add_edge("manager", "title_generator")
    graph.add_edge("manager", "tags_extractor")
    graph.add_edge("manager", "web_search_references_generator")

    # All Level 2 nodes -> Reviewer (Level 3)
    graph.add_edge("tldr_generator", "reviewer")
    graph.add_edge("title_generator", "reviewer")
    graph.add_edge("tags_extractor", "reviewer")
    graph.add_edge("web_search_references_generator", "reviewer")

    # Conditional edges from reviewer
    graph.add_conditional_edges(
        "reviewer",
        route_from_reviewer,
        {
            "revision_dispatcher": "revision_dispatcher",
            "end": END,
        },
    )

    # Revision dispatcher routes to all level 2 nodes in parallel for revision
    # Each node will check internally if it needs to run based on approval status
    graph.add_edge("revision_dispatcher", "tldr_generator")
    graph.add_edge("revision_dispatcher", "title_generator")
    graph.add_edge("revision_dispatcher", "tags_extractor")
    graph.add_edge("revision_dispatcher", "web_search_references_generator")

    return graph.compile()


def visualize_graph(graph: StateGraph, save_path: str = OUTPUTS_DIR):
    """Visualize the content processing graph."""
    print("📊 Visualizing the content processing graph...")
    print(graph.get_graph().draw_mermaid())

    # Save the graph as PNG
    try:
        png = graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
        with open(os.path.join(save_path, "content_processing_graph.png"), "wb") as f:
            f.write(png)
        print(
            f"✅ Graph saved to {os.path.join(save_path, 'content_processing_graph.png')}"
        )
    except Exception as e:
        print(f"⚠️ Could not save graph image: {e}")


def run_content_processing(text: str) -> Dict[str, Any]:
    """
    Convenience function to run the content processing graph.

    Args:
        text: The text content to process

    Returns:
        Dictionary containing all processing results
    """
    # Create initial state
    initial_state = ContentProcessingState(
        text=text,
        tldr=None,
        title=None,
        tags=None,
        references=[],
        references_content=[],
        selected_references=[],
        manager_decision=None,
        revision_round=0,
        needs_revision=None,
        tldr_feedback=None,
        title_feedback=None,
        references_feedback=None,
        tldr_approved=None,
        title_approved=None,
        references_approved=False,
    )

    # Create and run the graph
    graph = create_content_processing_graph()
    visualize_graph(graph)
    final_state = graph.invoke(initial_state)

    return final_state


if __name__ == "__main__":
    # Example usage with a sample text
    sample_text = """
    Machine learning has revolutionized artificial intelligence by enabling computers to learn 
    from data without explicit programming. Deep learning, a subset of machine learning, 
    uses neural networks with multiple layers to process complex patterns in data. 
    Popular frameworks like TensorFlow and PyTorch have made it easier for researchers 
    and practitioners to implement these algorithms. Recent advances in transformer 
    architectures, particularly models like GPT and BERT, have shown remarkable 
    performance in natural language processing tasks. These developments have been 
    documented in numerous papers published in conferences like NeurIPS and ICML.
    """

    print("=" * 80)
    print("🚀 CONTENT PROCESSING WORKFLOW DEMO")
    print("=" * 80)

    results = run_content_processing(text=sample_text)

    print("\n" + "=" * 80)
    print("📋 FINAL PROCESSING RESULTS")
    print("=" * 80)

    if results:
        print(f"\n\n📌 Title: {results.get('title', 'N/A')}")
        print(f"\n\n📝 TLDR: {results.get('tldr', 'N/A')}")
        print(f"\n\n🏷️ Tags: {', '.join(results.get('tags', []))}")
        print(f"\n\n📚 References: {(results.get('references', []))}")
    else:
        print("❌ No results generated")
