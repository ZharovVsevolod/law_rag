from law_rag.build_graph import document_split
from law_rag.knowledge.graph_building import get_triplets_from_text
from law_rag.documents.common import list_files_in_foler, save_pkl
from law_rag.models.llm_wrapper import get_llm_model

from law_rag.config import Settings

from langchain_core.exceptions import OutputParserException

from tqdm import tqdm
from dotenv import load_dotenv

def generate_triplets():
    # Model
    model_chain = get_llm_model(
        model_type = Settings.models.llm_model_type,
        engine = Settings.models.llm_engine,
        answer_parser = "json",
        inside_docker_container = False # TODO Development: Change to True (just remove this line) for docker
    )

    # Initialization of all triplets of chunks
    all_triplets_list = []

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
        
            # Save answers every 150 steps just in case
            if pc % 50 == 0:
                save_pkl(all_triplets_list, Settings.documents.holmes_pickle)
                print("Interim saving...")
            pc += 1
    
    # Final save
    save_pkl(all_triplets_list, Settings.documents.holmes_pickle)



if __name__ == "__main__":
    load_dotenv()
    generate_triplets()