"""There is stored some functions for preparing the chunks (in Langchain Document type) to load in Neo4j graph database"""

from langchain_core.documents import Document

from law_rag.documents.md_parser import find_all_markdown_links
from law_rag.neo4j.node_schema import Node, Article, Paragraph, Subparagraph

from law_rag.config import Settings

from typing import Dict, Literal, Tuple, List


def get_chunk_specification(document: Document) -> Node:
    """Define the chunk specification to get some node information for setting up the Graph Database

    Chunk specification contains this parameters:
    - **type**: str - node type. Can be Article, Paragraph or Subparagraph;
    - **number**: str - chunk number based on it's serial number.  
        Structure is `<Codex Number>`.`<Article Number>`.`<Paragraph Number>`.`<Subparagraph NUmber>` depends on what type is it;
    - **previous**: str - previous chunk number, if it is exists. Otherwise is set to *None*;
    - **parents**: List[str] - list of parent numbers (types that higher in the hierarchy);
    - **text**: str - chunk main text
    - **has_reference**: bool - if the text contains some markdown links ([some link](www.some-link.com)), 
        parameter will be set to *True*, otherwise - *False*;
    - **references**: List[Tuple[str, str]] - if the text contains some markdown links, there will be list of them.  
        It has tuple structure, like (some_link, www.some-link.com).
    
    Metadata of the chunk should have this parameters:
    - **Codex**: str (but it have to be a number, like "149")
    - **Article**: str (starts with "**Статья X. ...")
    - **Paragraph**: str, optional* (starts with "1.", "3.1.", ...)
    - **Subparagraph**: str, optional* (starts with "1)", "г)", ...)

    \* - depends on the type of the chunk.

    It is returned one of this Node classes:
    - Article
    - Paragraph
    - Subparagraph

    depends on a node type (the level specified based on the document metadata).
    
    Arguments
    ---------
    document: Document
        The chunk of Langchain Document type with some metadata
    
    Returns
    -------
    builded_node: Node
        The node for Neo4j with all specification
    """
    # Find out the Node Type (it is also the metadata level extraction too)
    if "Subparagraph" in document.metadata:
        level = "Subparagraph"
    elif "Paragraph" in document.metadata:
        level = "Paragraph"
    elif "Article" in document.metadata:
        level = "Article"
    
    chunk_number, previous, parents = get_chunk_number(document.metadata, level)

    if level != "Article":
        text = document.page_content
        if Settings.data.clean_text_from_links:
            references, text = find_all_markdown_links(text)
        else:
            references = find_all_markdown_links(text)
    
    
    match level:
        case "Article":
            builded_node = Article(
                number = chunk_number,
                previous = previous,
                parents = parents,
                name = document.page_content
            )

        case "Paragraph":
            builded_node = Paragraph(
                number = chunk_number,
                previous = previous,
                parents = parents,
                text = text,
                has_reference = bool(references),
                references = references
            )

        case "Subparagraph":
            builded_node = Subparagraph(
                number = chunk_number,
                previous = previous,
                parents = parents,
                text = text,
                has_reference = bool(references),
                references = references
            )

    return builded_node


def get_chunk_number(
    document_metadata: Dict[str, str],
    level: Literal["Article", "Paragraph", "Subparagraph"]
) -> Tuple[str, str | None, List[str]]:
    """Get the chunk number and the previous chunk number and the parent chunk numbers
    
    Based on chunk metadata this function is pull out information about serial chunk numbers.

    The number structure generates due this rule:
    - `<Codex Number>`.`<Article Number>`.`<Paragraph Number>`.`<Subparagraph NUmber>`

    depends on what level is the chunk

    Chunk metadata should have this parameters:
    - **Codex**: str (but it have to be a number, like "149");
    - **Article**: str (starts with "**Статья X. ..."), where X - is a number of article;
    - **Paragraph**: str, optional* (starts with "1.", "3.1.", ...);
    - **Subparagraph**: str, optional* (starts with "1)", "г)", ...).

    Arguments
    ---------
    document_metadata: Dict[str, str]
        The chunk metadata. The structure is desribed higher
    level: Literal["Article", "Paragraph", "Subparagraph"]
        Chunk hierarchycal level
    
    Returns
    -------
    chunk_number: str
        Number of this chunk
    previous: str | None
        Previous chunk number, if it is exists.  
        If the number of this particular chunk is 1st, parameter is set to None
    parents: List[str]
        Parent chunk numbers (chunks that types is higher in the hierarchy)
    """
    chunk_numbers = [document_metadata["Codex"]]

    # The Article level
    # [1] - the Article number, because it always starts with "**Статья 2. ..."
    # [:-1] - remove the dot in the end of the number
    chunk_numbers.append(document_metadata["Article"].split(" ")[1][:-1])

    # The Paragraph level
    # [-1] - the Paragraph number, because it generates as "Пункт 3"
    if level in ["Paragraph", "Subparagraph"]:
        try:
            chunk_numbers.append(document_metadata["Paragraph"].split(" ")[-1])
        except Exception:
            pass
    
    # The Subparagraph level
    # [-1] - the Subparagraph number, because it generates as "Подпункт 4"
    if level in ["Subparagraph"]:
        chunk_numbers.append(document_metadata["Subparagraph"].split(" ")[-1])
    
    # Self number
    chunk_number = ".".join(chunk_numbers)

    # Parents
    parents = []
    n = len(chunk_numbers)
    for i in range(2, n):
        parent_number = ".".join(chunk_numbers[:i])
        parents.append(parent_number)

    # Previous number
    previous = None
    if level != "Article":
        previous = int(chunk_numbers[-1]) - 1
        if previous == 0:
            previous = None
        else:
            previous = parents[-1] + f".{previous}"

    return chunk_number, previous, parents
