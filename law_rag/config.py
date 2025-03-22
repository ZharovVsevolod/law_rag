from pathlib import Path
from pydantic import BaseModel
from omegaconf import OmegaConf

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

class Config(BaseModel):
    documents: Docs


# Load the yaml config file
def _load_yaml_config(path: Path):
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