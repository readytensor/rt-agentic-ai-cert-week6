import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OUTPUTS_DIR = os.path.join(ROOT_DIR, "outputs")

DATA_DIR = os.path.join(ROOT_DIR, "data")

CONFIG_DIR = os.path.join(ROOT_DIR, "config")

CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, "config.yaml")

PROMPT_CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, "prompt_config.yaml")

PREDEFINED_ENTITIES_FILE_PATH = os.path.join(CONFIG_DIR, "predefined_entities.yaml")
