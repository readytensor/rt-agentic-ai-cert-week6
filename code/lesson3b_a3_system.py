from typing import Any, Dict, Sequence
import os
from pprint import pprint

from graphs.a3_graph import build_a3_graph
from states.a3_state import initialize_a3_state
from utils import load_publication_example, load_config
from langgraph_utils import save_graph_visualization
from consts import (
    MANAGER,
    LLM_TAGS_GENERATOR,
    TAG_TYPE_ASSIGNER,
    TAGS_SELECTOR,
    TLDR_GENERATOR,
    TITLE_GENERATOR,
    REFERENCES_GENERATOR,
    REFERENCES_SELECTOR,
    REVIEWER,
)


def run_a3_graph(text: str) -> Dict[str, Any]:
    """
    Runs the A3 agentic authoring graph with the provided LLM and configurations.
    """

    # Load configurations
    a3_config = load_config()["a3_system"]

    # # Initialize state
    initial_state = initialize_a3_state(
        input_text=text,
        manager_prompt_cfg=a3_config["agents"][MANAGER]["prompt_config"],
        llm_tags_generator_prompt_cfg=a3_config["agents"][LLM_TAGS_GENERATOR][
            "prompt_config"
        ],
        tag_type_assigner_prompt_cfg=a3_config["agents"][TAG_TYPE_ASSIGNER][
            "prompt_config"
        ],
        tags_selector_prompt_cfg=a3_config["agents"][TAGS_SELECTOR]["prompt_config"],
        tag_types=a3_config["tag_types"],
        max_tags=a3_config["max_tags"],
        title_gen_prompt_cfg=a3_config["agents"][TITLE_GENERATOR]["prompt_config"],
        tldr_gen_prompt_cfg=a3_config["agents"][TLDR_GENERATOR]["prompt_config"],
        references_gen_prompt_cfg=a3_config["agents"][REFERENCES_GENERATOR][
            "prompt_config"
        ],
        max_search_queries=a3_config["max_search_queries"],
        references_selector_prompt_cfg=a3_config["agents"][REFERENCES_SELECTOR][
            "prompt_config"
        ],
        max_references=a3_config["max_references"],
        reviewer_prompt_cfg=a3_config["agents"][REVIEWER]["prompt_config"],
        max_revisions=a3_config["max_revisions"],
    )

    # # Build the graph
    graph = build_a3_graph(a3_config)
    save_graph_visualization(graph, graph_name="a3_system")

    # Run the graph
    final_state = graph.invoke(initial_state)
    return final_state


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
    sample_text = load_publication_example(1)  # ⚠️ CAUTION: SEE NOTE ABOVE

    response = run_a3_graph(sample_text)

    print("=" * 80)
    print("🔍 A3-SYSTEM DEMO")
    print("=" * 80)
    print("Manager brief:")
    print(response["manager_brief"])
    print("=" * 80)
    print("Title:")
    print(response["title"])
    print("=" * 80)
    print("TL;DR:")
    print(response["tldr"])
    print("=" * 80)
    print("Tags:")
    pprint(response["selected_tags"])
    print("=" * 80)
    print("Search queries:")
    pprint(response["reference_search_queries"])
    print("=" * 80)
    print("References:")
    print("Selected # of references:", len(response["selected_references"]))
    for ref in response["selected_references"]:
        print(f"Title: {ref['title']}")
        print(f"URL: {ref['url']}")
        print("-" * 40)
    print("=" * 80)
