import re
import spacy
from typing import List, Dict, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.language_models import BaseChatModel
import multiprocessing
from llm import get_llm
from prompt_builder import build_prompt_from_config
from utils import load_config
from paths import GAZETTEER_ENTITIES_FILE_PATH, PROMPT_CONFIG_FILE_PATH
from state_and_types import Entities

# Cap max_workers between 1 and (available CPUs - 2)
available_cpus = multiprocessing.cpu_count()
max_allowed_workers = max(1, available_cpus - 2)
print(f"Using a maximum of {max_allowed_workers} workers for parallel processing.")


EXCLUDED_SPACY_ENTITY_TYPES = {"DATE", "CARDINAL"}

prompt_config = load_config(PROMPT_CONFIG_FILE_PATH)["entity_extraction"]


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


def extract_entities_llm(
    text: str,
    entity_types: List[str],
    model_name: str = "gpt-4o-mini",
    chunk_size: int = 4024,
    chunk_overlap: int = 256,
    entity_batch_size: int = 10,
    parallelize: bool = False,
    max_workers: int = max_allowed_workers,
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
        parallelize: Whether to parallelize extraction using ThreadPoolExecutor
        max_workers: Number of workers to use for parallelization

    Returns:
        List of extracted entities, each represented as a dictionary.
    """
    llm = get_llm(model_name)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    results = []

    def process_chunk_batch(chunk, batch_types):
        return _extract_entities_from_chunk(chunk, batch_types, llm)

    if parallelize:
        futures = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for chunk in chunks:
                for i in range(0, len(entity_types), entity_batch_size):
                    batch_types = entity_types[i : i + entity_batch_size]
                    futures.append(
                        executor.submit(process_chunk_batch, chunk, batch_types)
                    )

            for future in tqdm(
                as_completed(futures), total=len(futures), desc="LLM extraction"
            ):
                try:
                    results.extend(future.result())
                except Exception as e:
                    print(f"Error in extraction task: {e}")
    else:
        for chunk in tqdm(chunks, desc="LLM extraction"):
            for i in range(0, len(entity_types), entity_batch_size):
                batch_types = entity_types[i : i + entity_batch_size]
                results.extend(process_chunk_batch(chunk, batch_types))

    for entity in results:
        entity["method"] = "llm"

    return results


def extract_entities_spacy(
    text: str,
) -> List[Dict[str, str]]:
    """
    Extract unique named entities from the input text using spaCy's transformer model.

    Args:
        text: The input text to analyze for entities

    Returns:
        List of deduplicated extracted entities, each represented as a dictionary.
    """
    model = spacy.load("en_core_web_trf")
    seen = set()
    results = []

    for ent in model(text).ents:
        if ent.label_ in EXCLUDED_SPACY_ENTITY_TYPES:
            continue
        key = (ent.text.lower(), ent.label_)
        if key not in seen:
            seen.add(key)
            results.append(
                {
                    "name": ent.text.lower(),
                    "type": ent.label_,
                    "method": "encoder",
                }
            )

    return results


def extract_entities_gazetteer(text: str) -> List[Dict[str, str]]:
    """
    Extracts unique entities from the text based on a predefined list (gazetteer).
    Pure regex-based extraction. Deduplicates results based on entity name and type.

    Args:
        text: The input text string.

    Returns:
        A list of unique extracted entities, each represented as a dictionary.
    """
    entities = load_config(GAZETTEER_ENTITIES_FILE_PATH)
    if not text:
        return []

    seen = set()
    deduped_entities = []

    for entity_name, entity_type in entities.items():
        pattern = r"\b" + re.escape(entity_name) + r"\b"

        try:
            for _ in re.finditer(pattern, text, re.IGNORECASE):
                key = (entity_name.lower(), entity_type)
                if key not in seen:
                    seen.add(key)
                    deduped_entities.append(
                        {
                            "name": entity_name.lower(),
                            "type": entity_type,
                            "method": "gazetteer",
                        }
                    )
        except re.error as e:
            print(f"Regex error for entity '{entity_name}': {e}")
            continue

    return deduped_entities
