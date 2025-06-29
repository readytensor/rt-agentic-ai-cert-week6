"""
LangGraph implementation for multi-method entity extraction.
This graph orchestrates three different entity extraction methods and aggregates their results.
"""

from typing import Dict, Any

from tools import (
    extract_entities_llm,
    extract_entities_spacy,
    extract_entities_gazetteer,
)

from states_types.entity_extraction import EntityExtractionState, Entities
from utils import load_config
from paths import CONFIG_FILE_PATH
from llm import get_llm

config = load_config(CONFIG_FILE_PATH)

MAX_ENTITIES = config.get("max_entities", 5)


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
