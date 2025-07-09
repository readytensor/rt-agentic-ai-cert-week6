from typing import Any, Dict
from langgraph.graph import StateGraph, START, END


from consts import (
    MANAGER,
    TLDR_GENERATOR,
    TITLE_GENERATOR,
    REFERENCES_GENERATOR,
    REFERENCES_SELECTOR,
    REVIEWER,
)
from states.a3_state import A3SystemState
from graphs.tag_generation_graph import add_tag_generation_flow
from nodes.a3_nodes import (
    make_manager_node,
    make_title_generator_node,
    make_tldr_generator_node,
    make_references_generator_node,
    make_references_selector_node,
    make_reviewer_node,
    route_from_reviewer,
)


def build_a3_graph(a3_config: Dict[str, Any]) -> StateGraph:
    """
    Creates and returns the agentic authoring graph with hierarchical structure and feedback loop.
    """
    # Create the graph
    graph = StateGraph(A3SystemState)

    # -------------------------------------------------------------------------------
    # ADD NODES
    manager_node = make_manager_node(llm_model=a3_config["agents"][MANAGER]["llm"])
    graph.add_node(MANAGER, manager_node)

    # worker nodes to generate title, TLDR, and references
    title_gen_node = make_title_generator_node(
        llm_model=a3_config["agents"][TITLE_GENERATOR]["llm"]
    )
    graph.add_node(TITLE_GENERATOR, title_gen_node)

    tldr_gen_node = make_tldr_generator_node(
        llm_model=a3_config["agents"][TLDR_GENERATOR]["llm"]
    )
    graph.add_node(TLDR_GENERATOR, tldr_gen_node)

    references_generator_node = make_references_generator_node(
        llm_model=a3_config["agents"][REFERENCES_GENERATOR]["llm"]
    )
    graph.add_node(REFERENCES_GENERATOR, references_generator_node)

    references_selector_node = make_references_selector_node(
        llm_model=a3_config["agents"][REFERENCES_SELECTOR]["llm"]
    )
    graph.add_node(REFERENCES_SELECTOR, references_selector_node)

    # Add reviewer node
    reviewer_node = make_reviewer_node(llm_model=a3_config["agents"][REVIEWER]["llm"])
    graph.add_node(REVIEWER, reviewer_node)

    # -------------------------------------------------------------------------------
    # ADD EDGES AND FLOWS

    graph.add_edge(START, MANAGER)

    graph.add_edge(MANAGER, TITLE_GENERATOR)
    graph.add_edge(MANAGER, TLDR_GENERATOR)
    graph.add_edge(MANAGER, REFERENCES_GENERATOR)
    graph.add_edge(REFERENCES_GENERATOR, REFERENCES_SELECTOR)

    # Add tag generation flow
    tag_gen_exit_node = add_tag_generation_flow(
        graph=graph,
        entry_node=MANAGER,
        tag_generation_config=a3_config,
    )

    graph.add_edge(tag_gen_exit_node, END)
    graph.add_edge([TITLE_GENERATOR, TLDR_GENERATOR, REFERENCES_SELECTOR], REVIEWER)

    graph.add_conditional_edges(
        REVIEWER,
        route_from_reviewer,
        {
            TLDR_GENERATOR: TLDR_GENERATOR,
            TITLE_GENERATOR: TITLE_GENERATOR,
            REFERENCES_GENERATOR: REFERENCES_GENERATOR,
            "end": END,
        },
    )

    return graph.compile()
