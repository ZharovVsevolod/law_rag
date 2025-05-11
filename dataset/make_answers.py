import sys
import pandas as pd

from law_rag.documents.common import save_pkl
from law_rag.models.llm_wrapper import get_llm_model, retriever_answer
from law_rag.knowledge.db_connection import langchain_neo4j_vector
from law_rag.models.blanks import QA_ANSWER_SYSTEM_PROMPT
from law_rag.config import Settings
from config import DatasetSettings

from langchain.schema import HumanMessage

from tqdm import tqdm
from dotenv import load_dotenv

from langchain_neo4j import Neo4jVector
from langchain_core.runnables.base import RunnableSerializable
from typing import Literal, List, Dict


def load_dataset(path: str) -> pd.DataFrame:
    qa_dataset = pd.read_csv(path, index_col = 0)
    return qa_dataset

def save_to_dataset(dataset: pd.DataFrame, name: str, values: List[str]) -> None:
    dataset[name] = values
    dataset.to_csv(DatasetSettings.qa_dataset.csv("answers_save_path"))


def separate_raw_retirever_answer(retiever_answer: str) -> List[str]:
    return retiever_answer.split("\n\n")

def get_answer(
    question: str,
    model: RunnableSerializable,
    vector_graph: List[Neo4jVector] | Neo4jVector | None,
    mode: Literal["blank", "naive", "holmes", "full"],
) -> Dict[str, str | List[str]]:
    match mode:
        case "blank":
            retriever_message = question
        
        case "naive":
            retriever_message, raw_retriever_message = retriever_answer(
                question = question,
                retriever = vector_graph,
                return_also_raw_answer = True
            )

        case "holmes":
            retriever_message = retriever_answer(
                question = question,
                retriever = vector_graph,
                ship_headers = True
            )
        
        case "full":
            retriever_message_naive, raw_retriever_message = retriever_answer(
                question = question,
                retriever = vector_graph[0],
                return_also_raw_answer = True
            )
            retriever_message_holmes = retriever_answer(
                question = question,
                retriever = vector_graph[1],
                ship_headers = True
            )
            retriever_message = retriever_message_naive + "\n\n" + retriever_message_holmes
    
    message = [QA_ANSWER_SYSTEM_PROMPT , HumanMessage(retriever_message)]
    answer = model.invoke(message)

    match mode:
        case "full" | "naive":
            raw_retriever_message = separate_raw_retirever_answer(raw_retriever_message)
            return {
                "answer": answer,
                "raw_retriever": raw_retriever_message
            }
        
        case "blank" | "holmes":
            return {"answer": answer}


def answers(
    mode: Literal["blank", "naive", "holmes", "full"]
):
    if not Settings.system.silent_creation:
        print(f"Mode: {mode}")

    # Initialization
    qa_dataset = load_dataset(DatasetSettings.qa_dataset.csv("path_to_save"))
    if not Settings.system.silent_creation:
        print("Dataset was loaded")

    model = get_llm_model(
        model_type = Settings.models.llm_model_type,
        engine = Settings.models.llm_engine,
        answer_parser = "string",
        inside_docker_container = False
    )

    match mode:
        case "blank":
            vector_graph = None
        
        case "naive":
            vector_graph = langchain_neo4j_vector("naive")
        
        case "holmes":
            vector_graph = langchain_neo4j_vector("holmes")
        
        case "full":
            vector_graph = [
                langchain_neo4j_vector("naive"),
                langchain_neo4j_vector("holmes")
            ]
    
    if not Settings.system.silent_creation:
        print("Connection to dataset was established")

    answers = []
    if mode in ["naive", "full"]:
        raw_retrievers = []
    pc = 0

    # Proceeding
    for index, row in tqdm(qa_dataset.iterrows(), total = qa_dataset.shape[0]):
        returned_answer = get_answer(
            question = row["question"],
            model = model,
            vector_graph = vector_graph,
            mode = mode
        )

        answers.append(returned_answer["answer"])
        if mode in ["naive", "full"]:
            raw_retrievers.append(returned_answer["raw_retriever"])
        
        # Save answers every 20 steps just in case
        if pc % 20 == 0:
            save_pkl(answers, DatasetSettings.qa_dataset.answers_save_path)
            if mode in ["naive", "full"]:
                save_pkl(raw_retrievers, DatasetSettings.qa_dataset.raw_save_path)
        pc += 1
    
    
    # Saving
    save_pkl(answers, DatasetSettings.qa_dataset.answers_save_path)
    if mode in ["naive", "full"]:
        save_pkl(raw_retrievers, DatasetSettings.qa_dataset.raw_save_path)



if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise RuntimeError("To proper work of this script need 1 additional argument - mode of retriever. It could be blank, naive, holmes or full")

    if sys.argv[1] not in ["blank", "naive", "holmes", "full"]:
        raise RuntimeError("To proper work of this script need 1 additional argument - mode of retriever. It could be blank, naive, holmes or full")

    load_dotenv()
    answers(mode = sys.argv[1])