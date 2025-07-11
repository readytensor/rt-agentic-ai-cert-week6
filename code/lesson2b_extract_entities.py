from typing import Any, Dict

from pprint import pprint

from states.tag_generation_state import (
    initialize_tag_generation_state,
)
from graphs.tag_generation_graph import build_tag_generation_graph
from utils import load_publication_example, load_config
from langgraph_utils import save_graph_visualization

from consts import (
    LLM_TAGS_GENERATOR,
    TAG_TYPE_ASSIGNER,
    TAGS_SELECTOR,
)


def run_tag_generation_graph(text: str) -> Dict[str, Any]:
    """
    Runs the A3 agentic authoring graph with the provided LLM and configurations.

    Args:
        text (str): The input text to process for tag generation.

    Returns:
        Dict[str, str]: The final state containing generated tags and their types.
    """
    # Load configurations
    config = load_config()["tags_generation"]

    # # Initialize state
    initial_state = initialize_tag_generation_state(
        input_text=text,
        llm_tags_generator_prompt_cfg=config["agents"][LLM_TAGS_GENERATOR][
            "prompt_config"
        ],
        tag_type_assigner_prompt_cfg=config["agents"][TAG_TYPE_ASSIGNER][
            "prompt_config"
        ],
        tags_selector_prompt_cfg=config["agents"][TAGS_SELECTOR]["prompt_config"],
        tag_types=config["tag_types"],
        max_tags=config["max_tags"],
    )

    # Build the graph
    graph = build_tag_generation_graph(config)
    save_graph_visualization(graph, graph_name="tag_generation")

    # Run the graph
    final_state = graph.invoke(initial_state)
    return final_state


if __name__ == "__main__":

    # ⚠️⚠️⚠️ CAUTION: LONG + POTENTIALLY EXPENSIVE INPUTS ⚠️⚠️⚠️
    # -------------------------------------------------------------------------------
    # For quick texting, use example 1. Example 1 is short and will run quickly and cheaply.
    # 🚨 Publication examples 2 and 3 are large and may take 1 or 2 minutes to process.
    # 💸 They will consume a lot of tokens (~40k for example 2) which could cost you a few cents
    #     depending on your LLM.
    # 👉 For faster and cheaper runs:
    #    - Use example 1
    #    - Or create shorter versions of examples 2 and 3
    # ✅ This project is for learning — don’t burn through tokens unnecessarily.
    # -------------------------------------------------------------------------------
    # Example usage
    sample_text = load_publication_example(1)  # ⚠️ CAUTION: SEE NOTE ABOVE

    response = run_tag_generation_graph(sample_text)

    print("=" * 80)
    print("🔍 MULTI-METHOD ENTITY EXTRACTION DEMO")
    print("=" * 80)
    print("LLM Tags:")
    pprint(response["llm_tags"])
    print("=" * 80)
    print("spaCy Tags:")
    pprint(response["spacy_tags"])
    print("=" * 80)
    print("Gazetteer Tags:")
    pprint(response["gazetteer_tags"])
    print("=" * 80)
    print("Candidate Tags:")
    pprint(response["candidate_tags"])
    print("=" * 80)
    print("🎯 FINAL EXTRACTED ENTITIES")
    pprint(response["selected_tags"])
    print("=" * 80)
    print(f"\nTotal unique tags extracted: {len(response['selected_tags'])}")
    print("✅ Tag generation completed successfully.")
    # -------------------------------------------------------------------------------
