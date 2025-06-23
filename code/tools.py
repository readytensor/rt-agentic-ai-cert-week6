import re
import spacy
from typing import List, Dict, Optional, Any, Callable
from langchain_core.tools import tool
from concurrent.futures import ThreadPoolExecutor
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from llm import get_llm
from prompt_builder import build_prompt_from_config
from utils import load_config
from paths import PREDEFINED_ENTITIES_FILE_PATH, PROMPT_CONFIG_FILE_PATH

prompt_config = load_config(PROMPT_CONFIG_FILE_PATH)["entity_extraction"]


class Entity(BaseModel):
    name: str = Field(description="The entity name")
    type: Optional[str] = Field(
        description="The entity type or 'none of the above' if not confidently classified."
    )
    description: str = Field(
        description="A comprehensive description of the entity and its attributes"
    )


class Entities(BaseModel):
    entities: List[Entity] = Field(
        description="The extracted entities. Can be empty if no entities are found.",
    )


def _extract_entities_from_chunk(
    text: str,
    entity_types: Optional[List[str]],
    llm: BaseChatModel,
) -> List[Dict[str, str]]:
    """
    Extract entities from the input text chunk.

    Args:
        text: Input text to extract entities from
        entity_types: list of entity types to extract (e.g., ["algorithm", "dataset", "tool"])
        llm: The language model to use for extraction

    Returns:
        List of extracted entities, each represented as a dictionary
    """
    all_entities = []

    entity_types_with_none_of_the_above = entity_types + ["none of the above"]
    input_data = f"<text>\n{text}</text>\n<entity_types>\n{entity_types_with_none_of_the_above}</entity_types>\n"

    prompt = build_prompt_from_config(prompt_config, input_data=input_data)
    response = llm.with_structured_output(Entities).invoke(prompt).model_dump()

    all_entities.extend(
        [i for i in response["entities"] if i["type"] != "none of the above"]
    )

    for entity in all_entities:
        entity["name"] = entity["name"].lower()

    return all_entities


@tool
def extract_entities_llm(
    text: str,
    entity_types: List[str],
    model_name: str = "gpt-4o-mini",
    chunk_size: int = 1024,
    chunk_overlap: int = 128,
    entity_batch_size: int = 2,
    parallelize: bool = False,
    max_workers: int = 4,
) -> List[Dict[str, str]]:
    """
    Extract entities from the input text using recursive chunking.

    Args:
        text: The input text to analyze
        entity_types: List of entity types to extract
        model_name: Name of the LLM model to use
        chunk_size: Maximum size of each text chunk
        chunk_overlap: Number of characters to overlap between chunks
        entity_batch_size: Number of entity types to process in each batch
        loop_retries: Number of retry attempts for each extraction
        parallelize: Whether to parallelize extraction using ThreadPoolExecutor
        max_workers: Number of workers to use for parallelization

    Returns:
        List of extracted entities, each represented as a Node object.
    """
    # Initialize the LLM
    llm = get_llm(model_name)

    # Use recursive text splitter for chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)

    results = []

    if parallelize:

        def process_chunk_batch(chunk, batch_types):
            return _extract_entities_from_chunk(prompt_config, chunk, batch_types, llm)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for chunk in chunks:
                for i in range(0, len(entity_types), entity_batch_size):
                    batch_types = entity_types[i : i + entity_batch_size]
                    futures.append(
                        executor.submit(process_chunk_batch, chunk, batch_types)
                    )

            for future in futures:
                results.extend(future.result())
    else:
        for chunk in chunks:
            for i in range(0, len(entity_types), entity_batch_size):
                batch_types = entity_types[i : i + entity_batch_size]
                results.extend(_extract_entities_from_chunk(chunk, batch_types, llm))

    # Add method to entities and convert to Node objects
    for entity in results:
        entity["method"] = "llm"

    return results


@tool
def extract_entities_spacy(
    text: str,
) -> List[Dict[str, str]]:
    """
    Extract named entities from the input text using spaCy's transformer model.

    Args:
        text: The input text to analyze for entities

    Returns:
        List of extracted entities, each represented as a Entity object.
    """
    model = spacy.load("en_core_web_trf")
    return [
        {
            "name": ent.text.lower(),
            "type": ent.label_,
            "method": "encoder",
        }
        for ent in model(text).ents
    ]


@tool
def extract_entities_predefined(text: str) -> List[Dict[str, str]]:
    """
    Extracts entities from the text based on a predefined list of entities.

    Args:
        text: The input text string.

    Returns:
        A list of extracted entities, each represented as a dictionary.
    """
    entities = load_config(PREDEFINED_ENTITIES_FILE_PATH)
    found_entities = []
    if not text:
        return found_entities

    for entity_name, entity_type in entities.items():
        # Create pattern that matches only the entity name
        pattern = r"\b" + re.escape(entity_name) + r"\b"

        try:
            # Find all non-overlapping matches in the text
            for _ in re.finditer(pattern, text, re.IGNORECASE):
                # Append the found entity using its canonical name and type
                found_entities.append(
                    {
                        "name": entity_name.lower(),
                        "type": entity_type,
                        "method": "predefined",
                    }
                )
        except re.error as e:
            print(f"Regex error for entity '{entity_name}': {e}")
            continue

    return found_entities
