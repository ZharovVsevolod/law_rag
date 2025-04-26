from law_rag.knowledge.node_schema import Node
from law_rag.knowledge.node_schema import get_parent_type

# -----------------
# Creation commands
# -----------------

def delete_all_nodes() -> str:
    """
    ```Cypher
    MATCH (n)
    OPTIONAL MATCH (n)-[r]-()
    DELETE n,r
    ```
    """
    command = """
    MATCH (n)
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
    command = f"MERGE (n:{node.type}" + " {" + f'{key_name}: "{key_value}"' + "})\n"

    # Set of parameters that do not need to set. 
    # Primal key is set already, system parameter do not need to set at all
    do_not_set_params = node.system_parameters() + [key_name]

    # Set the remaining Node parameters
    for param_name in node.all_parameters():
        # Check if we need to set this parameter
        if param_name not in do_not_set_params:
            param_value = getattr(node, param_name)

            # If the parameter is String - we need to set double quotes at the start and the end for Neo4j
            if type(param_value) is str:
                command += f'SET n.{param_name} = "{param_value}"\n'
            else:
                command += f"SET n.{param_name} = {param_value}\n"
    
    return command


def create_previous_relationship(node: Node) -> str:
    """
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
    command = f"MERGE (n:{node.type}" + " {" + f'{key_name}: "{key_value}"' + "})\n"

    previous_value = node.previous
    command += f"MERGE (n_prev:{node.type}" + " {" + f'{key_name}: "{previous_value}"' + "})\n"

    command += "MERGE (n_prev)-[r:NEXT]->(n)\n"
    
    return command


def create_parent_relationship(node: Node) -> str:
    """
    The command will be based on this schema:
    ```Cypher
    MERGE (n:<type_of_node> {<key_name>: <key_value>})

    MERGE (n_parent:<parent_type_of_node> {<key_name>: <parent_key_value>})
    MERGE (n)-[r:PART_OF]->(n_parent)
    ```
    """
    key_name, key_value = node.primal_key()
    command = f"MERGE (n:{node.type}" + " {" + f'{key_name}: "{key_value}"' + "})\n"

    parent_type = get_parent_type(node)

    command += f"MERGE (n_p:{parent_type}" + " {" + f'{key_name}: "{node.parent}"' + "})\n"
    command += f"MERGE (n)-[r:PART_OF]->(n_p)\n"
    
    return command