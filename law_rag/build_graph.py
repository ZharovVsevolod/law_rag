"""
Build the Graph Database in Neo4j
"""

from law_rag.knowledge.db_connection import langchain_neo4j_connection, langchain_embeddings
from law_rag.documents.md_parser import document_split
from law_rag.knowledge.graph_building import get_chunk_specification, get_chunk_number
from law_rag.knowledge.commands import (
    create_node_command, 
    create_parent_relationship, 
    create_previous_relationship,
    delete_all_nodes,
    delete_index,
    create_embeddings_label
)
from law_rag.documents.common import list_files_in_foler
from law_rag.knowledge.node_schema import Codex, Article

from law_rag.config import Settings

from tqdm import tqdm
from dotenv import load_dotenv


def build_graph_from_scratch() -> None:
    """Build the Graph Database in Neo4j

    This very one function will build the whole knowledge graph  
    from the markdown file. This file should be prompted in config file  
    in this path:
    ```
    config/config.yaml
    ```

    Steps
    -----
    - Connect to Neo4j database instance
    - Clear Database
    - Get Codex folder and path to file
    - Create Codex Node
    - Create all other Nodes
        - Get the next codex text point
        - Get the point specification
        - Check if an Article that point belongs to is exists
            - If not, creates one
            - And create a relationship with Codex Node
        - Get and run create node command
        - Get create previous node relationship command
            - And run it if previous node exists
        - Get and run create parents relationships command
    """
    # Connect to Neo4j database instance
    graph = langchain_neo4j_connection()

    # Clear Database
    graph.query(delete_index())
    graph.query(delete_all_nodes())
    if not Settings.system.silent_creation:
        print("Database was cleared for build from scratch")
        print()

    # Get Codex folder and path to file
    codexes = list_files_in_foler(Settings.documents.path_to_folder)
    for codex in codexes:
        print(f"Codex: {codex}")

        # Create Codex Node
        node = Codex(
            number = codex,
            name = f"{codex}-ФЗ",
            previous = None,
            parent = None
        )
        command = create_node_command(node)
        graph.query(command)
        if not Settings.system.silent_creation:
            print("The Codex Node was created")

        # Get the Codex text
        texts = document_split(codex)
        start_chunk = Settings.data.start_chunk[codex]
        texts = texts[start_chunk:]
        if not Settings.system.silent_creation:
            print("Get all Codex text in chunks")
            print("Proceed through all chunks...")

        # Create all other Nodes
        # Some necessary parameters
        existing_articles = []

        # Get the next codex text point
        for text in tqdm(texts):
            # Get the point specification
            specs = get_chunk_specification(text)

            if specs is not None:
                # Check if an Article that point belongs to is exists
                # Because info about Articles we have in metadata :/
                article = text.metadata["Article"]
                if article not in existing_articles and "Статья" in article:
                    # If not, create one
                    article_number, article_previous, _ = get_chunk_number(text.metadata, level = "Article")
                    node = Article(
                        number = article_number,
                        name = article,
                        previous = article_previous,
                        parent = codex
                    )
                    command = create_node_command(node)
                    graph.query(command)
                    # And create a relationship with Codex Node
                    command = create_parent_relationship(node)
                    graph.query(command)
                    
                    # Now that Article Node is exists
                    existing_articles.append(article)

                # Get and run create node command
                command = create_node_command(specs)
                graph.query(command)

                # Get create previous node relationship command
                command = create_previous_relationship(specs)
                # Run it is it's not a "None" string
                if command != "None":
                    graph.query(command)

                # Get and run create parents relationships command
                command = create_parent_relationship(specs)
                graph.query(command)
        
        if not Settings.system.silent_creation:
            print()
            print(f"Knowledge Graph for {codex}-ФЗ was created")
            print("-----")
            print()
    
    # Create the very one embeddings node label with MultiLabel feature
    if not Settings.system.silent_creation:
        print("Creating MultiLabel for Embeddings...")
    command = create_embeddings_label(
        union_label = Settings.data.embeddings_label,
        labels = ["Article", "Paragraph", "Subparagraph"]
    )
    graph.query(command)

    # Close the connection because we need another connection instance 
    # for creating an embeddings
    graph.close()

    # And build embeddings
    build_embeddings()


def build_embeddings():
    # Create embeddings
    if not Settings.system.silent_creation:
        print("Creating embeddings...")
        print(f"Model: {Settings.models.embeddings_name}")
        print("Please, wait...")
    
    vector_graph = langchain_embeddings()

    if not Settings.system.silent_creation:
        print("Embeddings was created")

        answer = vector_graph.similarity_search(
            query = "Что такое информация?"
        )
        for ans in answer:
            print(ans)
            print("-----")
            print()



if __name__ == "__main__":
    load_dotenv()
    build_graph_from_scratch()