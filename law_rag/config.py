"""
The specification and load for the yaml config file. It is using OmegaConf for yaml hierarchical structure.

Most of the time you'll need the `Settings` variable with configuration specification.

You can run this .py file to print the config file and check if it is loaded correctly.
"""

from pathlib import Path
from pydantic import BaseModel
from omegaconf import OmegaConf, DictConfig

import logging
logger = logging.getLogger(__name__)

# Get the path to the yaml config file
pwd = Path(__file__).parent.parent
config_file = pwd / "config" / "config.yaml"


# The whole structure of configuration
class Docs(BaseModel):
    path_to_folder: str
    path_to_pdf: str
    path_to_html: str
    path_to_md: str
    path_to_md_cleaned: str

class Data(BaseModel):
    name: str

class Config(BaseModel):
    documents: Docs
    data: Data


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