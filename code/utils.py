import yaml
import os

from paths import CONFIG_FILE_PATH, DATA_DIR, OUTPUTS_DIR
from llm import get_llm


def load_config(config_path: str = CONFIG_FILE_PATH):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_publication_example(example_number: int) -> str:
    """
    Load a publication example text file.

    Args:
        example_number: The number of the example to load (1, 2, or 3)

    Returns:
        The content of the publication example file
    """
    example_fpath = f"publication_example{example_number}.md"
    full_path = os.path.join(DATA_DIR, example_fpath)
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()
