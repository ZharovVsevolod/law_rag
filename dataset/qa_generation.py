import pandas as pd

from law_rag.build_graph import document_split
from law_rag.documents.common import list_files_in_foler, save_pkl
from law_rag.models.llm_wrapper import get_llm_model
from law_rag.models.blanks import SYNTHETIC_QA_DATASET_SYSTEM_PROMPT, human_qa_dataset

from law_rag.config import Settings
from config import DatasetSettings

from langchain_core.exceptions import OutputParserException
from typing import List, Dict

from tqdm import tqdm

def save_as_csv(qa_dt: List[Dict[str, str]]) -> None:
    questions = []
    answers = []
    context = []
    difficulty = []

    for item in qa_dt:
        questions.append(item["question"])
        answers.append(item["answer"])
        context.append(item["context"])
        difficulty.append(item["difficulty"])
    
    qa_dataset = pd.DataFrame({
        "question": questions,
        "answer": answers,
        "context": context,
        "difficulty": difficulty
    })

    path_to_save = DatasetSettings.qa_dataset.path_to_save.split(".")[0] + ".csv"
    qa_dataset.to_csv(path_to_save, index_label = "id")


def generate_qa_dataset() -> None:
    # Model
    model_chain = get_llm_model(
        model_type = Settings.models.llm_model_type,
        engine = Settings.models.llm_engine,
        answer_parser = "json",
        inside_docker_container = False # This may usually use outside docker container
    )

    # Initialization of all triplets of chunks
    all_questions: List[Dict[str, str]] = []

    # Get Codex folder and path to file
    codexes = list_files_in_foler(Settings.documents.path_to_folder)
    for codex in codexes:
        print(f"Codex: {codex}")
        
        # Get the Codex text
        texts = document_split(codex, mode = "holmes")
        start_chunk = Settings.data.start_chunk[codex]
        texts = texts[start_chunk:]
        
        if not Settings.system.silent_creation:
            print("Get all Codex text in chunks")
            print("Proceed through all chunks...")
        
        pc = 0 # pc but not enumerate for tqdm proper work
        for text in tqdm(texts):
            try:
                human = human_qa_dataset(
                    text = text.page_content, 
                    num_questions = DatasetSettings.qa_dataset.num_questions_per_chunk
                )
                messages = [SYNTHETIC_QA_DATASET_SYSTEM_PROMPT, human]
                answer = model_chain.invoke(messages)
                all_questions += answer
            
            except OutputParserException:
                # In this case usually there are no useful text to generate answer
                pass
        
            # Save answers every 20 steps just in case
            if pc % 20 == 0:
                save_pkl(all_questions, DatasetSettings.qa_dataset.path_to_save)
            pc += 1
        
    # Final save
    save_pkl(all_questions, DatasetSettings.qa_dataset.path_to_save)
    save_as_csv(all_questions)


if __name__ == "__main__":
    generate_qa_dataset()