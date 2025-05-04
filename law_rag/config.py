"""
The specification and load for the yaml config file. It is using OmegaConf for yaml hierarchical structure.

Most of the time you'll need the `Settings` variable with configuration specification.

You can run this .py file to print the config file and check if it is loaded correctly.
"""

from pathlib import Path
from pydantic import BaseModel
from omegaconf import OmegaConf, DictConfig

from typing import Dict, Literal

import logging
logger = logging.getLogger(__name__)

# Get the path to the yaml config file
pwd = Path(__file__).parent.parent
config_file = pwd / "config" / "config.yaml"


# The whole configuration structure
class Docs(BaseModel):
    path_to_folder: str
    path_to_pdf: str
    path_to_md: str
    path_to_md_cleaned: str

    def pdf(self, codex_name: str):
        return self.path_to_folder + "/" + codex_name + "/" + self.path_to_pdf
    
    def md(self, codex_name: str):
        return self.path_to_folder + "/" + codex_name + "/" + self.path_to_md

    def md_clean(self, codex_name: str):
        return self.path_to_folder + "/" + codex_name + "/" + self.path_to_md_cleaned


class Data(BaseModel):
    start_chunk: Dict[str, int]
    clean_text_from_links: bool
    link_placeholder: str
    embeddings_label: str
    embeddings_parameter: str
    index_name: str

class System(BaseModel):
    silent_creation: bool
    logging_file: str
    # LEVELS: 10 - Debug, 20 - Info, 30 - Warning, 40 - Error, 50 - Critical Error
    logging_level: Literal[10, 20, 30, 40, 50]

class Models(BaseModel):
    embeddings_model: str
    embeddings_dimension: int
    similarity_function: Literal["cosine", "euclidean"]
    llm_base_url: str
    llm_model_type: Literal["qwen3:8b", "deepseek-r1:8b", "gemma3:4b", "gemma2"]
    llm_engine: Literal["ollama"]

class Api(BaseModel):
    host: str
    port: int

class WebCfg(BaseModel):
    run_name: str
    path_to_history: str

class Config(BaseModel):
    documents: Docs
    data: Data
    system: System
    models: Models
    api: Api
    web: WebCfg


# Load the yaml config file
def _load_yaml_config(path: Path) -> DictConfig:
    """Load the yaml config file from the specific path.
    
    This function using OmegaConf for yaml hierarchical structure opportunity.
    
    Arguments
    ---------
    path: Path
        Path to the .yaml config file
    
    Returns
    -------
    config: DictConfig
        The config dictionary
    
    Raises
    ------
    FileNotFoundError
        If there is no .yaml config file in provided path
    """
    try:
        return OmegaConf.load(path)

    except FileNotFoundError as error:
        message = f"Error! There is no yaml file in {path}"
        logger.exception(message)
        raise FileNotFoundError(error, message) from error

Settings = Config(**_load_yaml_config(config_file))



if __name__ == "__main__":
    # We can run this .py file to check if the Settings was loaded correctly
    print(Settings)