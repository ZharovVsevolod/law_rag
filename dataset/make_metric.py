import numpy as np
import pandas as pd

from law_rag.models.embeddings_wrapper import HuggingFaceEmbeddings
from law_rag.config import Settings
from config import DatasetSettings

from tqdm import tqdm

from typing import List

def load_dataset(path: str) -> pd.DataFrame:
    qa_dataset = pd.read_csv(path, index_col = 0)
    return qa_dataset


def make_embeddings(texts: List[str], model: HuggingFaceEmbeddings) -> List[List[int]]:
    embeddgins = model.embed_documents(texts)
    return embeddgins


def similarity_score(A: List[int], B: List[int]) -> float:
    A = np.array(A)
    B = np.array(B)

    dot_product = np.dot(A, B)
    magnitude_A = np.linalg.norm(A)
    magnitude_B = np.linalg.norm(B)

    cosine_similarity = dot_product / (magnitude_A * magnitude_B)
    return cosine_similarity


def main():
    dataset = load_dataset(DatasetSettings.qa_dataset.path_to_full_save_csv)
    model = HuggingFaceEmbeddings(Settings.models.embeddings_model)

    if not Settings.system.silent_creation:
        print("Dataset and model were loaded")

    similarity_blank = []
    similarity_full = []
    similarity_naive = []
    similarity_triplets = []
    similarity_retriever = []
    pc = 0

    for index, row in tqdm(dataset.iterrows(), total = dataset.shape[0]):
        embeddings = make_embeddings(
            texts = [
                row["answer"], # 0
                row["context"], # 1
                row["blank_answer"], # 2
                row["full_answer"], # 3
                row["naive_answer"], # 4
                row["triplets_answer"], # 5
                row["retriever_1"], # 6
                row["retriever_2"], # 7
                row["retriever_3"] # 8
            ],
            model = model
        )

        s_blank = similarity_score(embeddings[0], embeddings[2])
        s_full = similarity_score(embeddings[0], embeddings[3])
        s_naive = similarity_score(embeddings[0], embeddings[4])
        s_triplets = similarity_score(embeddings[0], embeddings[5])

        s_retriever_1 = similarity_score(embeddings[1], embeddings[6])
        s_retriever_2 = similarity_score(embeddings[1], embeddings[7])
        s_retriever_3 = similarity_score(embeddings[1], embeddings[8])
        # Looking for best match
        s_retriever = np.max([s_retriever_1, s_retriever_2, s_retriever_3])

        similarity_blank.append(s_blank)
        similarity_full.append(s_full)
        similarity_naive.append(s_naive)
        similarity_triplets.append(s_triplets)
        similarity_retriever.append(s_retriever)

        # Save answers every 50 steps just in case
        if pc % 50 == 0:
            results = pd.DataFrame({
                "similarity_blank": similarity_blank,
                "similarity_full": similarity_full,
                "similarity_naive": similarity_naive,
                "similarity_triplets": similarity_triplets,
                "similarity_retriever": similarity_retriever,
            })
            results.to_csv(DatasetSettings.qa_dataset.path_to_results, index_label = "id")
        pc += 1
    
    if not Settings.system.silent_creation:
        print("Saving...")
    
    results = pd.DataFrame({
        "similarity_blank": similarity_blank,
        "similarity_full": similarity_full,
        "similarity_naive": similarity_naive,
        "similarity_triplets": similarity_triplets,
        "similarity_retriever": similarity_retriever,
    })
    results.to_csv(DatasetSettings.qa_dataset.path_to_results, index_label = "id")

    if not Settings.system.silent_creation:
        print(f"Results saved in {DatasetSettings.qa_dataset.path_to_results}")

    show_results()


def show_results():
    results = load_dataset(DatasetSettings.qa_dataset.path_to_results)

    print(f"Blank similarity score: {results["similarity_blank"].mean()}")
    print(f"Full RAG similarity score: {results["similarity_full"].mean()}")
    print(f"Naive KG RAG similarity score: {results["similarity_naive"].mean()}")
    print(f"RAG on triplets similarity score: {results["similarity_triplets"].mean()}")
    print(f"Retriever context similarity score: {results["similarity_retriever"].mean()}")



if __name__ == "__main__":
    show_results()