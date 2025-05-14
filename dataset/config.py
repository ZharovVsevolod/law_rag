from pathlib import Path
from pydantic import BaseModel

from law_rag.config import _load_yaml_config

from typing import Literal

# Get the path to the yaml config file
pwd = Path(__file__).parent.parent
dataset_config_file = pwd / "config" / "config.yaml"

class QaDatasetConfig(BaseModel):
    num_questions_per_chunk: int
    path_to_save: str
    answers_save_path: str
    raw_save_path: str
    path_to_full_save_csv: str
    path_to_results: str

    def csv(
        self, 
        path: Literal["path_to_save", "answers_save_path", "raw_save_path"]
    ) -> str:
        match path:
            case "path_to_save":
                return self.path_to_save.split(".")[0] + ".csv"
            case "answers_save_path":
                return self.answers_save_path.split(".")[0] + ".csv"
            case "raw_save_path":
                return self.raw_save_path.split(".")[0] + ".csv"
    
    def answers(
        self, 
        who: Literal["blank", "naive", "triplets", "full"],
        raw: bool = False
    ):
        if raw:
            parent_path = str(Path(self.raw_save_path).parent)
        else:
            parent_path = str(Path(self.answers_save_path).parent)
        
        return parent_path + f"/answers_{who}.pkl"


class DatasetConfig(BaseModel):
    qa_dataset: QaDatasetConfig


DatasetSettings = DatasetConfig(**_load_yaml_config(dataset_config_file))


if __name__ == "__main__":
    # We can run this .py file to check if the Settings was loaded correctly
    print(DatasetSettings)