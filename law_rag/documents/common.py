from langchain_core.documents import Document
from typing import List, Union

def load_text(path: str) -> List[str]:
    with open(
        file = path,
        mode = "r",
        encoding = "utf-8"
    ) as file:
        texts = file.readlines()
    
    return texts

def save_text(texts: List[str], save_path: str) -> None:
    with open(
        file = save_path,
        mode = "w+t",
        encoding = "utf-8"
    ) as file:
        file.writelines(texts)

def merge_text(texts: List[str]) -> str:
    full_text = "".join(texts)
    return full_text

def set_metadata_to_documents(
        param_name: str, 
        param_value: Union[int, float, str], 
        docs: List[Document]
    ) -> List[Document]:
    for doc in docs:
        doc.metadata[param_name] = param_value
    return docs