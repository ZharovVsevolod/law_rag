import pandas as pd
from law_rag.documents.common import load_pkl
from config import DatasetSettings
from typing import List

def split_raw(raw_item: List[str]) -> List[str]:
    match len(raw_item):        
        case 4:
            return raw_item[:3]
        
        case 6:
            splitted = []

            splitted.append(raw_item[1])
            splitted.append(raw_item[3])
            
            item_3rd = "".join(raw_item[4].split("\n")[2:])
            splitted.append(item_3rd)
            return splitted

        case _:
            return raw_item


def merge():
    # Dataset
    qa_dataset = pd.read_csv(DatasetSettings.qa_dataset.csv("path_to_save"), index_col = 0)

    # Answers
    answers_blank = load_pkl(DatasetSettings.qa_dataset.answers("blank"))
    answers_full = load_pkl(DatasetSettings.qa_dataset.answers("full"))
    answers_naive = load_pkl(DatasetSettings.qa_dataset.answers("naive"))
    answers_triplets = load_pkl(DatasetSettings.qa_dataset.answers("triplets"))

    # Retirever answers
    raw_full = load_pkl(DatasetSettings.qa_dataset.answers("full", raw = True))

    retriever_1 = []
    retriever_2 = []
    retriever_3 = []
    for item in raw_full:
        item = split_raw(item)
        retriever_1.append(item[0])
        retriever_2.append(item[1])
        retriever_3.append(item[2])

    # New dataset columns
    qa_dataset["blank_answer"] = answers_blank
    qa_dataset["full_answer"] = answers_full
    qa_dataset["naive_answer"] = answers_naive
    qa_dataset["triplets_answer"] = answers_triplets

    qa_dataset["retriever_1"] = retriever_1
    qa_dataset["retriever_2"] = retriever_2
    qa_dataset["retriever_3"] = retriever_3

    # Saving
    qa_dataset.to_csv(DatasetSettings.qa_dataset.path_to_full_save_csv, index_label = "id")


if __name__ == "__main__":
    merge()