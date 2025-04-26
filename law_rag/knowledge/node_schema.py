from pydantic import BaseModel
from typing import List, Tuple

class Node(BaseModel):
    """BaseNode class for the all custom Node types for GraphRAG project

    This pydantic-based class set all the necessary parameters and methods that every Node needs.

    Parameters
    ----------
    number: str
        The unique number of this Node
    previous: str | None
        Previous chunk number (if exists, it could be None if this chunk if the first in block)
    parent: str
        Parent number   
        (parents - higher level classes. For example, Article for Paragraph Node type)  
        It could be *None* if this is a Codex node
    type: str
        This is a property function. That parameter returned the Node type depends on it's class.  
        This parameter does not include in `all_parameters` method.  
        Should be override in every child class.
    
    Methods
    -------
    **primal_key**() -> *Tuple[str, str]*:
        Returns node primal key name and value.  
        Usually it is number parameter, but could be override in unique Node
    **all_parameters**() -> *set[str]*:
        Returns a set of all contained parameters
    **system_parameters**() -> *List[str]*:
        Returns a list of parameters names that used for relationships, not for Node parameters in Neo4j
    
    """
    number: str
    previous: str | None
    parent: str | None

    @property
    def type(self) -> str:
        """This is a property function. That parameter returned the Node type depends on it's class.

        For example, for base Node class it will return "BaseNode".  
        For Codex it should return "Codex", for Article - "Article", etc.

        This parameter should be override in every child class.

        This parameter does not include in `all_parameters` method.
        """
        return "BaseNode"

    def primal_key(self) -> Tuple[str, str]:
        """Returns name and parameter of the node primal key.  
        Usually it is a number parameter, but it could be override in a child class.

        Returns
        -------
        (name, value): Tuple[str, str]
            Node primal key name and value.
        """
        return "number", self.number

    def all_parameters(self) -> set[str]:
        """Returns a set of all contained parameters.  
        This doesn't contain property methods (type, for example).
        
        Returns
        -------
        model_fields_set: set[str]
            Set of all contained parameters
        """
        return self.model_fields_set
    
    def system_parameters(self) -> List[str]:
        """Returns a list of parameters names that used for relationships, not for Node parameters in Neo4j
        
        In base conception it is "previous" and "parent", but could be override for every child Node if needs.

        Returns
        -------
        system_params: List[str]
            System Node parameters
        """
        return ["previous", "parent"]

# -----

class Codex(Node):
    """Codex node
    
    Node for the highest level in project hierarchy.  
    Usually it is created non-automate for every case.

    Parameters
    ----------
    number: str
        The unique number of this Node
    name: str
        Codex name.  
        Usually it is just a number, like "149", which is means "149-ФЗ"
    """
    name: str

    @property
    def type(self):
        return "Codex"


class Article(Node):
    """Article Node

    Node for an Article block in Codex.
    
    Parameters
    ----------
    number: str
        The unique number of this Node
    name: str
        Article name.  
        Usually it is contains word "Статья", number and headline
    
    And some system parameters

    previous: str | None
        *System parameter*. Previous chunk number (if exists, it could be None if this chunk if the first in block)
    parent: str
        *System parameter*. Parent numbers  
        (parents - higher level classes. For example, Article for Paragraph Node type)  
        It could be *None* if this is a Codex node
    """
    name: str

    @property
    def type(self):
        return "Article"


class Paragraph(Node):
    """Paragraph Node
    
    Node for each paragraph in Article
    
    Parameters
    ----------
    number: str
        The unique number of this Node
    text: str
        Text of this particular paragraph
    has_reference: bool
        If the text contains some markdown links (link's structure in markdown looks like [some link](www.some-link.com)),  
        parameter will be set to *True*, otherwise - *False*
    references: List[Tuple[str, str]]
        If the text contains some markdown links, there will be list of them.  
        It has tuple structure, like (some_link, www.some-link.com).
    
    And some system parameters

    previous: str | None
        *System parameter*. Previous chunk number (if exists, it could be None if this chunk if the first in block)
    parent: str
        *System parameter*. Parent number  
        (parents - higher level classes. For example, Article for Paragraph Node type)  
        It could be *None* if this is a Codex node
    """
    text: str
    has_reference: bool
    references: List[Tuple[str, str]]

    @property
    def type(self):
        return "Paragraph"
    
    def system_parameters(self) -> List[str]:
        return super().system_parameters() + ["references"]


class Subparagraph(Node):
    """Subparagraph Node
    
    Node for each subparagraph in Paragraph
    
    Parameters
    ----------
    number: str
        The unique number of this Node
    text: str
        Text of this particular subparagraph
    has_reference: bool
        If the text contains some markdown links (link's structure in markdown looks like [some link](www.some-link.com)),  
        parameter will be set to *True*, otherwise - *False*
    references: List[Tuple[str, str]]
        If the text contains some markdown links, there will be list of them.  
        It has tuple structure, like (some_link, www.some-link.com).
    
    And some system parameters

    previous: str | None
        *System parameter*. Previous chunk number (if exists, it could be None if this chunk if the first in block)
    parent: str
        *System parameter*. Parent number  
        (parents - higher level classes. For example, Codex and Article for Paragraph Node type)  
        It could be *None* if this is a Codex node
    """
    text: str
    has_reference: bool
    references: List[Tuple[str, str]]

    @property
    def type(self):
        return "Subparagraph"
    
    def system_parameters(self) -> List[str]:
        return super().system_parameters() + ["references"]

# -----------------

def get_parent_type(node: Node) -> str:
    match node.type:
        case "Article":
            return "Codex"
        
        case "Paragraph":
            return "Article"
        
        case "Subparagraph":
            return "Paragraph"