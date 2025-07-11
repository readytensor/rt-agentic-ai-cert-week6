from typing import Callable, Dict, Any
from langgraph.graph import StateGraph
from langchain_core.runnables.graph import MermaidDrawMethod
import os

from llm import get_llm
from paths import OUTPUTS_DIR


def with_llm_node(
    llm_model: str,
    handler_factory: Callable[[Any], Callable[[Dict[str, Any]], Dict[str, Any]]],
) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """
    Creates a LangGraph-compatible node by injecting an LLM into a handler factory.

    Args:
        llm_model: Name of the LLM model.
        handler_factory: A function that accepts an LLM instance and returns a node function.

    Returns:
        A node function compatible with LangGraph.
    """
    llm = get_llm(llm_model)
    return handler_factory(llm)


def save_graph_visualization(
    graph: StateGraph,
    save_dir: str = OUTPUTS_DIR,
    graph_name: str = "graph",
):
    """Render and save the LangGraph structure as a Mermaid-based PNG image."""
    try:
        png = graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{graph_name}.png")
        with open(save_path, "wb") as f:
            f.write(png)
        print(f"✅ Graph saved to {save_path}")
    except Exception as e:
        print(f"⚠️ Could not save graph image: {e}")
