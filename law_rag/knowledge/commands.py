"""
Cypher commands for Neo4j Database
"""
# Cheet Sheet for Cypher commands
# https://neo4j.com/docs/cypher-cheat-sheet/5/all/#_merge

from law_rag.knowledge.node_schema import Node
from law_rag.knowledge.node_schema import get_parent_type
from law_rag.config import Settings

from typing import List, Literal, Dict

# -----------------
# Creation commands
# -----------------

def merge_command(
    node_name: str,
    node_type: str,
    param_name: str,
    param_value: str
) -> str:
    command = f"MERGE ({node_name}:{node_type}" + " {" + f'{param_name}: "{param_value}"' + "})\n"
    return command

def delete_index(
    mode: Literal["all", "naive", "holmes"] = "all"
) -> str:
    match mode:
        case "all":
            command = f"""
            DROP INDEX `{Settings.data.index_name}` IF EXISTS
            DROP INDEX `{Settings.data.holmes_index_name}` IF EXISTS
            """

        case "naive":
            command = f"DROP INDEX `{Settings.data.index_name}` IF EXISTS"
        
        case "holmes":
            command = f"DROP INDEX `{Settings.data.holmes_index_name}` IF EXISTS"

    return command

def delete_nodes(
    mode: Literal["all", "naive", "holmes"] = "all"
) -> str:
    """A Cypher command to clear all the graph and delete all nodes in it
    
    Command:
    ```Cypher
    MATCH (n)
    OPTIONAL MATCH (n)-[r]-()
    DELETE n,r
    ```
    """
    match mode:
        case "all":
            command = """
            OPTIONAL MATCH (n)
            OPTIONAL MATCH (n)-[r]-()
            DELETE n,r
            """

        case "naive":
            command = f"""
            OPTIONAL MATCH (n:Codex|Article|Paragraph|Subparagraph)
            OPTIONAL MATCH (n)-[r]-()
            DELETE n,r
            """
        
        case "holmes":
            command = f"""
            MATCH (n:{Settings.data.holmes_node})
            OPTIONAL MATCH (n)-[r]-()
            DELETE n,r
            """
    
    return command

def create_node_command(node: Node) -> str:
    """Returns a whole command to create a Node with nessasary parameters
    
    The command will be based on this schema:
    ```Cypher
    MERGE (n:<type_of_node> {<key_name>: <key_value>})
    SET n.<parameter_name> = <parameter_value>
    SET n.<parameter_name> = <parameter_value>
    ...
    SET n.<parameter_name> = <parameter_value>
    ```

    Arguments
    ---------
    node: Node
        Node that need to be transformed to Cypher creation command
    
    Returns
    -------
    command: str
        Cypher creation command for the argument node
    """
    # Merge the Node with the first paramets - key value
    key_name, key_value = node.primal_key()
    command = merge_command("n", node.type, key_name, key_value)

    # Set of parameters that do not need to set. 
    # Primal key is set already, system parameter do not need to set at all
    do_not_set_params = node.system_parameters() + [key_name]

    # Set the remaining Node parameters
    for param_name in node.all_parameters():
        # Check if we need to set this parameter
        if param_name not in do_not_set_params:
            param_value = getattr(node, param_name)

            # Set parameter only if it is exists
            if param_value is not None:
                # If the parameter is String - we need to set double quotes at the start and the end for Neo4j
                if type(param_value) is str:
                    command += f'SET n.{param_name} = "{param_value}"\n'
                else:
                    command += f"SET n.{param_name} = {param_value}\n"
    
    return command

def create_previous_relationship(node: Node) -> str:
    """A command to create relationship `NEXT` based on current node number and previous one.

    The command will be based on this schema:
    ```Cypher
    MERGE (n:<type_of_node> {<key_name>: <key_value>})
    MERGE (n_prev:<type_of_node> {<key_name>: <parent_key_value>})
    MERGE (n_prev)-[r:NEXT]->(n)
    ```
    """
    # A Node could not have any previous Nodes because it is the first
    if node.previous is None:
        return "None"

    key_name, key_value = node.primal_key()
    command = merge_command("n", node.type, key_name, key_value)

    previous_value = node.previous
    command += merge_command("n_prev", node.type, key_name, previous_value)

    command += "MERGE (n_prev)-[r:NEXT]->(n)\n"
    
    return command

def create_parent_relationship(node: Node) -> str:
    """A command to create relationship `PART_OF` to the higher on hierarchy node.
    
    The command will be based on this schema:
    ```Cypher
    MERGE (n:<type_of_node> {<key_name>: <key_value>})

    MERGE (n_parent:<parent_type_of_node> {<key_name>: <parent_key_value>})
    MERGE (n)-[r:PART_OF]->(n_parent)
    ```
    """
    key_name, key_value = node.primal_key()
    command = merge_command("n", node.type, key_name, key_value)

    parent_type = get_parent_type(node)

    if node.parent is not None:
        command += merge_command("n_p", parent_type, key_name, node.parent)
        command += f"MERGE (n)-[r:PART_OF]->(n_p)\n"
    
    return command

# Because there are no variants to create a vector index in Neo4j for multiple labels, we unite this labels
# https://stackoverflow.com/questions/79578894/can-i-create-one-vector-index-for-multiple-labels-e-g-movie-and-person
def create_embeddings_label(
        union_label: str,
        labels: List[Literal["Codex", "Article", "Paragraph", "Subparagraph"]]
    ) -> str:
    all_labels = "|".join(labels)
    command = f"""
    MATCH (n:{all_labels})
    SET n:{union_label}
    """
    return command

def create_index_embeddings() -> str:
    """
    (!NB) Need a

    - NodeLabel
    - dimension
    - similarity
    - embeddingsParameter

    params to execute!
    """
    command = """
    CREATE VECTOR INDEX `node-embeddings` IF NOT EXISTS
    FOR (a:$NodeLabel) ON (a.$embeddingsParameter)
    OPTIONS {
        indexConfig: {
            `vector.dimensions`: $dimension,
            `vector.similarity_function`: $similarity
        }
    }
    """
    return command

def holmes_nodes_creation(entity: Dict[str, str]) -> str:
    """
    **(!NB)** Need an `entity` additional parameter, Dict wich contains
    - subject
    - relation
    - object

    fields
    """
    command = merge_command("s", Settings.data.holmes_node, "name", entity["subject"])
    command += merge_command("o", Settings.data.holmes_node, "name", entity["object"])
    command += f"MERGE (s) -[r:{entity["relation"]}]->(o)"
    return command

# --------------
# Retrieval part
# --------------

# https://medium.com/neo4j/implementing-rag-how-to-write-a-graph-retrieval-query-in-langchain-74abf13044f2
def retrieval_query() -> str:
    command = """
    WITH node AS doc, score as similarity
    ORDER BY similarity DESC LIMIT 5
    CALL(doc) {
        OPTIONAL MATCH (doc)<-[:PART_OF]-(inner:Paragraph|Subparagraph)
        OPTIONAL MATCH (prevDoc:Paragraph|Subparagraph)-[:NEXT]->(doc)
        OPTIONAL MATCH (doc)-[:NEXT]->(nextDoc:Paragraph|Subparagraph)
        RETURN prevDoc, doc AS document, nextDoc, collect(inner.text) AS innerPart
    }
    RETURN 
        coalesce(prevDoc.text + '\n', '') +
        coalesce(document.text, '') +
        coalesce(reduce(acc = '\n', item IN innerPart | acc || item || '\n'), '') +
        coalesce(nextDoc.text, '') as text,
        similarity as score,
        {source: document.number} AS metadata
    """
    return command

def holmes_retrieval_query() -> str:
    command = """
    WITH node AS doc, score as similarity
    ORDER BY similarity DESC LIMIT 3
    CALL(doc) {
        OPTIONAL MATCH (doc)-[r]-(another)
        RETURN doc AS entity, r, another as connected_entity
    }
    RETURN
        coalesce(entity.name + ' -' + type(r) + '-> ' + connected_entity.name, '') as text,
        similarity as score,
        {main: entity.name} AS metadata
    """
    return command
