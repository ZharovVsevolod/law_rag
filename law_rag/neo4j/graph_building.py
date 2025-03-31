from langchain_core.documents import Document

from law_rag.documents.md_parser import find_all_markdown_links

from law_rag.config import Settings

from typing import Dict, Literal


def get_chunk_specification(document: Document) -> Dict[str, str]:
    specification = {}

    # Find out the Node Type (the level of metadata extraction too)
    if "Subparagraph" in document.metadata:
        level = "Subparagraph"
    elif "Paragraph" in document.metadata:
        level = "Paragraph"
    elif "Article" in document.metadata:
        level = "Article"
    

    specification["type"] = level
    specification["number"] = get_chunk_number(document.metadata, level)
    specification["text"] = document.page_content
    
    if level != "Article":
        if Settings.data.clean_text_from_links:
            references, text_without_links = find_all_markdown_links(
                document.page_content, 
                return_cleaned_text = Settings.data.clean_text_from_links
            )
            specification["text"] = text_without_links
        
        else:
            references = find_all_markdown_links(
                document.page_content, 
                return_cleaned_text = Settings.data.clean_text_from_links
            )
        
        specification["has_reference"] = bool(references)
        specification["references"] = references

    return specification


def get_chunk_number(
    document_metadata: Dict[str, str],
    level: Literal["Article", "Paragraph", "Subparagraph"]
) -> str:
    chunk_numbers = [document_metadata["Codex"]]

    # The Article level
    # [1] - the number of the Article, because it always starts with "**Статья 2. ..."
    # [:-1] - remove the dot in the end of the number
    chunk_numbers.append(document_metadata["Article"].split(" ")[1][:-1])

    # The Paragraph level
    # [-1] - the number of the Paragraph, because it generates as "Пункт 3"
    if level in ["Paragraph", "Subparagraph"]:
        try:
            chunk_numbers.append(document_metadata["Paragraph"].split(" ")[-1])
        except Exception:
            pass
    
    # The Subparagraph level
    # [-1] - the number of the Subparagraph, because it generates as "Подпункт 4"
    if level in ["Subparagraph"]:
        chunk_numbers.append(document_metadata["Subparagraph"].split(" ")[-1])
    
    chunk_number = ".".join(chunk_numbers)
    return chunk_number


