from law_rag.documents.common import load_pkl
from law_rag.knowledge.db_connection import langchain_neo4j_connection, langchain_neo4j_vector
from law_rag.knowledge.commands import (
    delete_index,
    delete_nodes,
    holmes_nodes_creation
)
from law_rag.models.llm_wrapper import retriever_answer
from law_rag.config import Settings

from tqdm import tqdm
from dotenv import load_dotenv


def build_nodes():
    # Connect to Neo4j database instance
    graph = langchain_neo4j_connection()

    # Clear Database
    graph.query(delete_index("holmes"))
    graph.query(delete_nodes("holmes"))

    # Load file with nodes params
    triplets = load_pkl(Settings.documents.holmes_pickle)

    # Create every triplet
    for triplet in tqdm(triplets):
        command = holmes_nodes_creation(triplet)
        graph.query(command)
    
    # Update graph schema
    graph.refresh_schema()
    
    # Create embeddings for the new nodes
    build_embeddings()


def build_embeddings():
    # Create embeddings
    if not Settings.system.silent_creation:
        print("Creating embeddings...")
        print(f"Model: {Settings.models.embeddings_model}")
        print("Please, wait...")
    
    vector_graph = langchain_neo4j_vector("holmes")

    if not Settings.system.silent_creation:
        print("Embeddings was created and/or loaded")
        print()

        print("Check how it is working:")
        answer = retriever_answer(
            question = "Что такое информация?",
            retriever = vector_graph,
            ship_headers = True
        )
        print(answer)

        # -------
        # Cypher queries usually are the same and user may not be so kind
        # to provide exacly how the entity is named in database, so
        # it is a little bit not nessesary in this scenario
        # -------
        # chain = holmes_retriever_chain(
        #     graph = langchain_neo4j_connection(),
        #     model = get_llm_model(
        #         model_type = Settings.models.llm_model_type,
        #         engine = Settings.models.llm_engine,
        #         inside_docker_container = False # Development: Delete this line for True value
        #     )
        # )
        # answer = chain.invoke("Что такое информация?")
        # print(answer["result"])
        # -------



if __name__ == "__main__":
    load_dotenv()
    build_nodes()