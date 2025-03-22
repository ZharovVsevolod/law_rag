from typing import List

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