"""
Make the connection with database instance
"""

import os

from neo4j import GraphDatabase, Driver
from langchain_neo4j import Neo4jGraph

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
        uri = os.environ["DB_URI"], 
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
        url = os.environ["DB_URI"],
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


if __name__ == "__main__":
    load_dotenv()
    graph = langchain_neo4j_connection()