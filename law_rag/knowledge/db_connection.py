"""
Make the connection with database instance
"""
import os

from neo4j import GraphDatabase, Driver
from langchain_neo4j import Neo4jGraph, Neo4jVector

from law_rag.models.embeddings_wrapper import get_embeddings
from law_rag.knowledge.commands import retrieval_query, holmes_retrieval_query
from law_rag.config import Settings

from typing import Literal

from dotenv import load_dotenv

def check_connection() -> Driver:
    """Make the connection to Neo4j Database with original Neo4j driver
    
    Returns
    -------
    driver: neo4j.Driver
        Driver to the neo4j database
    
    Raises
    ------
    Exeption
        If the driver could not connect to a Neo4j database instance
    """
    # Get the connection to Neo4j Database
    driver = GraphDatabase.driver(
        uri = Settings.system.neo4j_base_url, 
        auth = (os.environ["DB_NAME"], os.environ["DB_PASSWORD"])
    )
    
    # Check the connection. If successful, return driver instance
    try:
        driver.verify_connectivity()
        print("Connection established")
        return driver

    except Exception as e:
        print("Error!")
        raise Exception(e)


def langchain_neo4j_connection() -> Neo4jGraph:
    """Make the connection to Neo4j Database with Langchain_neo4j plagin
    
    Returns
    -------
    graph: langchain_neo4j.Neo4jGraph
        Driver to the neo4j database
    
    Raises
    ------
    Exeption
        If the driver could not connect to a Neo4j database instance
    """
    # Get the connection to Neo4j Database
    graph = Neo4jGraph(
        url = Settings.system.neo4j_base_url,
        username = os.environ["DB_NAME"],
        password = os.environ["DB_PASSWORD"]
    )

    # Check the connection. If successful, return graph instance
    try:
        graph._check_driver_state()
        print("Connection established")
        return graph

    except Exception as e:
        print("Error!")
        raise Exception(e)


# https://python.langchain.com/docs/integrations/vectorstores/neo4jvector/
def langchain_neo4j_vector(mode: Literal["naive", "holmes"]) -> Neo4jVector:
    match mode:
        case "naive":
            vector_graph = Neo4jVector.from_existing_graph(
                embedding = get_embeddings(),

                url = Settings.system.neo4j_base_url,
                username = os.environ["DB_NAME"],
                password = os.environ["DB_PASSWORD"],

                index_name = Settings.data.index_name,
                node_label = Settings.data.embeddings_label,
                text_node_properties = ["text", "name"],
                embedding_node_property = Settings.data.embeddings_parameter,

                search_type = "hybrid",
                retrieval_query = retrieval_query()
            )
        
        case "holmes":
            vector_graph = Neo4jVector.from_existing_graph(
                embedding = get_embeddings(),

                url = Settings.system.neo4j_base_url,
                username = os.environ["DB_NAME"],
                password = os.environ["DB_PASSWORD"],

                index_name = Settings.data.holmes_index_name,
                node_label = Settings.data.holmes_node,
                text_node_properties = ["name"],
                embedding_node_property = Settings.data.embeddings_parameter,

                retrieval_query = holmes_retrieval_query()
            )

    return vector_graph



if __name__ == "__main__":
    load_dotenv()
    # Here we can check if the connection to Neo4j was successful
    graph = langchain_neo4j_connection()
    graph.close()