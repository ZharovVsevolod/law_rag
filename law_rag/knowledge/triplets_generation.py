from law_rag.build_graph import document_split
from law_rag.documents.common import list_files_in_foler, save_pkl
from law_rag.models.llm_wrapper import get_llm_model
from law_rag.models.blanks import HOLMES_SYSTEM_GET_TRIPLETS

from law_rag.config import Settings

from langchain.schema import HumanMessage

from langchain_core.documents import Document
from langchain_core.runnables.base import RunnableSerializable
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.schema import AIMessage
from langchain_core.exceptions import OutputParserException
from typing import List, Dict

from tqdm import tqdm
import logging


def get_triplets_from_text(
    text: str | Document,
    chain: BaseChatModel | RunnableSerializable
) -> AIMessage | List[Dict[str, str]]:
    if type(text) is Document:
        text = text.page_content

    human_message = HumanMessage(text)
    messages = [HOLMES_SYSTEM_GET_TRIPLETS, human_message]

    answer = chain.invoke(messages)
    return answer


def fix_generation_issues(triplets_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
    for triplet in triplets_list:
        try:
            triplet["relation"] = triplet["relation"].replace(" ", "_")
            triplet["relation"] = triplet["relation"].replace("/", "_")
            triplet["relation"] = triplet["relation"].replace(",", "")
            triplet["relation"] = triplet["relation"].replace("(", "")
            triplet["relation"] = triplet["relation"].replace(")", "")
            triplet["relation"] = triplet["relation"].replace("-", "_")
            triplet["relation"] = triplet["relation"].upper()
        except TypeError:
            del triplet
        except:
            logger.warning("Some error")
            logger.warning(triplet)
            pass
    
    return triplets_list


def generate_triplets():
    # Model
    model_chain = get_llm_model(
        model_type = Settings.models.llm_model_type,
        engine = Settings.models.llm_engine,
        answer_parser = "json",
        inside_docker_container = False # This may usually use outside docker container
    )

    # Initialization of all triplets of chunks
    all_triplets_list: List[Dict[str, str]] = []

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
                answer = get_triplets_from_text(text, model_chain)
                all_triplets_list += answer
            except OutputParserException:
                # In this case usually there are no useful text to get triplets from
                pass
        
            # Save answers every 50 steps just in case
            if pc % 50 == 0:
                save_pkl(all_triplets_list, Settings.documents.holmes_pickle)
                print("Interim saving...")
            pc += 1
    
    # Fix some answer issues
    all_triplets_list = fix_generation_issues(all_triplets_list)
    
    # Final save
    save_pkl(all_triplets_list, Settings.documents.holmes_pickle)


if __name__ == "__main__":
    # Logging point
    logging.basicConfig(
        filename = Settings.system.logging_file,
        encoding = "utf-8",
        filemode = "w+t",
        level = Settings.system.logging_level
    )
    logger = logging.getLogger(__name__)

    # Actual generation
    generate_triplets()