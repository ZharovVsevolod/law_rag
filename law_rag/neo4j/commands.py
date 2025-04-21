from law_rag.neo4j.node_schema import Node

def create_node_command(node: Node) -> str:
    """Returns a whole command to create a Node with nessasary parameters
    
    The command will be based on this schema:
    ```Cypher
    MATCH (node:<type_of_node> {<key_parameter_name>: <key_parameter_value>})
    SET node.<parameter_name> = <parameter_value>
    SET node.<parameter_name> = <parameter_value>
    ...
    SET node.<parameter_name> = <parameter_value>
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
    command = f"MATCH (node:{node.type}" + " {" + f'{key_name}: "{key_value}"' + "})\n"

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
                command += f'SET node.{param_name} = "{param_value}"\n'
            else:
                command += f"SET node.{param_name} = {param_value}\n"
    
    return command
