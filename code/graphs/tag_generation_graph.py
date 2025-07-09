from langgraph.graph import StateGraph, START, END
from typing import Any, Dict

from consts import (
    LLM_TAGS_GENERATOR,
    SPACY_TAGS_GENERATOR,
    GAZETTEER_TAGS_GENERATOR,
    TAG_TYPE_ASSIGNER,
    TAGS_AGGREGATOR,
    TAGS_SELECTOR,
)
from nodes.tag_generation import (
    make_llm_tag_generator_node,
    make_spacy_tag_generator_node,
    make_gazetteer_tag_generator_node,
    make_tag_type_assigner_node,
    aggregate_tags_node,
    make_tag_selector_node,
)
from states.tag_generation_state import (
    TagGenerationState,
)


def build_tag_generation_graph(tag_generation_config: Dict[str, Any]) -> StateGraph:
    graph = StateGraph(TagGenerationState)

    # Insert tag generation flow
    final_node = add_tag_generation_flow(
        graph=graph,
        entry_node=START,
        tag_generation_config=tag_generation_config,
    )

    graph.add_edge(final_node, END)
    return graph.compile()


def add_tag_generation_flow(
    graph: StateGraph,
    entry_node: str,
    tag_generation_config: Dict[str, Any],
) -> str:
    """
    Adds the tag generation flow into an existing LangGraph.

    Args:
        graph: The existing StateGraph to inject into.
        entry_node: The node in the existing graph after which the tag flow begins.
        tag_generation_config: Configuration dictionary for tag generation.

    Returns:
        str: The name of the final node in this subgraph (typically TAGS_SELECTOR).
    """
    # Create nodes
    llm_tags_generator_node = make_llm_tag_generator_node(
        llm_model=tag_generation_config["agents"][LLM_TAGS_GENERATOR]["llm"]
    )
    graph.add_node(LLM_TAGS_GENERATOR, llm_tags_generator_node)

    spacy_tag_generator_node = make_spacy_tag_generator_node()
    graph.add_node(SPACY_TAGS_GENERATOR, spacy_tag_generator_node)

    tag_type_assigner_node = make_tag_type_assigner_node(
        llm_model=tag_generation_config["agents"][TAG_TYPE_ASSIGNER]["llm"]
    )
    graph.add_node(TAG_TYPE_ASSIGNER, tag_type_assigner_node)

    gazetteer_tag_generator_node = make_gazetteer_tag_generator_node()
    graph.add_node(GAZETTEER_TAGS_GENERATOR, gazetteer_tag_generator_node)

    graph.add_node(TAGS_AGGREGATOR, aggregate_tags_node)

    tags_selector_node = make_tag_selector_node(
        llm_model=tag_generation_config["agents"][TAGS_SELECTOR]["llm"],
        max_tags=tag_generation_config["max_tags"],
    )
    graph.add_node(TAGS_SELECTOR, tags_selector_node)

    # Wire the subgraph
    graph.add_edge(entry_node, LLM_TAGS_GENERATOR)
    graph.add_edge(entry_node, SPACY_TAGS_GENERATOR)
    graph.add_edge(SPACY_TAGS_GENERATOR, TAG_TYPE_ASSIGNER)
    graph.add_edge(entry_node, GAZETTEER_TAGS_GENERATOR)

    graph.add_edge(
        [LLM_TAGS_GENERATOR, TAG_TYPE_ASSIGNER, GAZETTEER_TAGS_GENERATOR],
        TAGS_AGGREGATOR,
    )

    graph.add_edge(TAGS_AGGREGATOR, TAGS_SELECTOR)

    return TAGS_SELECTOR
