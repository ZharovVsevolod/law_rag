"""
Some function for parsing markdown file and preprocess it for the future graph database setup
"""
import re

from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document

from law_rag.config import Settings
from law_rag.documents.common import (
    load_text, 
    save_text, 
    merge_text, 
    set_metadata_to_documents
)

from typing import List, Optional, Tuple

import logging
logger = logging.getLogger(__name__)

def find_all_markdown_links(
    md_text: str, 
    return_cleaned_text: bool = False
) -> List[Tuple[str, str]] | Tuple[List[Tuple[str, str]], str]:
    # Some magic formula. I have got this from this source:
    # https://stackoverflow.com/questions/63197371/detecting-all-links-in-markdown-files-in-python-and-replace-them-with-outputs-of
    INLINE_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    links = list(INLINE_LINK_RE.findall(md_text))

    if return_cleaned_text:
        just_links = []
        for _, link in links:
            just_links.append(link)

        cleaned_md_text = remove_links_from_text(
            md_text,
            just_links,
            placeholder = Settings.data.link_placeholder
        )
        return links, cleaned_md_text

    return links

def remove_links_from_text(
    md_text: str, 
    links: List[str]| str,
    placeholder: str
) -> str:
    if type(links) is str:
        links = [links]
    
    for link in links:
        md_text = md_text.replace(link, placeholder)
    
    return md_text

def clean_headers(texts: List[str]) -> List[str]:
    """Delete markdown header markup (`#`) from the texts
    
    Arguments
    ---------
    texts: List[str]
        List of Markdown text that need to be cleaned from the headers
    
    Returns
    -------
    texts: List[str]
        List of Markdown text without any # symbols
    """
    for i, text in enumerate(texts):
        texts[i] = text.replace("#", "")
    
    return texts

def make_headers_for_article(texts: List[str]) -> List[str]:
    """Make new custom headers in the markdown texts of Russian Codex
    
    That function is setting programly up new headers in the markdown text based on:
    - The **Header 1** (`#`) is set for keyword "Статья" in the text (the name of article will be in the header text)
    - The **Header 2** (`##`) is set for Paragraph (with dots in the end, like "1.", "2.", "2.1.", etc.) with setting head keyword "## Пункт"
    - The **Header 3** (`###`) is set for Subparagraph (with brackets in the end, like "1)", "2)", "2.1)", etc.) with setting head keyword "### Подпункт"

    Arguments
    ---------
    texts: List[str]
        List of Markdown text of Russian Codex
    
    Returns
    -------
    texts: List[str]
        List of Markdown text with new custom headers
    """
    for i, text in enumerate(texts):
        if "Статья" in text:
            if text[0] == " ":
                text = text[1:]
            texts[i] = "# " + text
        
        else:
            digit = text.split(" ")[0]
            try:
                if digit[0] != "(":
                    match digit[-1]:
                        case ".":
                            texts[i] = f"## Пункт {digit[:-1]}\n" + text
                        case ")":
                            texts[i] = f"### Подпункт {digit[:-1]}\n" + text
            except Exception as e:
                pass
        
    return texts

def preprocessing(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None
) -> None:
    """Preprocess markdown text
    
    It includes:
    - Clean any headers from the text
    - Set up new custom headers

    You can specify the input and/or output paths.
    If you don't, the function will get it from the config file.

    Arguments
    ---------
    input_path: Optional[str] = None
        Path to the pdf file. If it is not specified, path will be pulled from the config file.
    output_path: Optional[str] = None
        Path where converted markdown file will be saved. If it is not specified, path will be pulled from the config file.
    """
    # If paths are not set manually - we get them from the Settings module (config file)
    if input_path is None:
        input_path = Settings.documents.path_to_md
    if output_path is None:
        output_path = Settings.documents.path_to_md_cleaned
    
    texts = load_text(input_path)
    logger.info("The file was loaded")

    texts = clean_headers(texts)
    logger.info("The headers was removed")

    texts = make_headers_for_article(texts)
    logger.info("The headers was created")

    save_text(texts, output_path)
    logger.info("The file was saved")

def document_split(
    path: Optional[str] = None,
    codex_name: Optional[str] = None
) -> List[Document]:
    """Split markdown text into Documents based on its heades
    
    This function split markdown text based on three levels of markdown headers:
    - The **Header 1** (`#`)
    - The **Header 2** (`##`)
    - The **Header 3** (`###`)

    and returns the List of Documents with some metadata that contains:
    - The Header 1 head of this peace of text
    - The Header 2 head of this peace of text (*if exists*)
    - The Header 3 head of this peace of text (*if exists*)
    - The name of the source ("Codex")

    Arguments
    ---------
    path: Optional[str] = None
        Path to markdown text. If it is not specified, path will be pulled from the config file.
    codex_name: Optional[str] = None
        The name of the source that will be set for "Codex" name in matadata. If it is not specified, it will be the name of the document.
    
    Returns
    -------
    markdown_text_header_split: List[Document]
        The splitted by headers markdown text
    """
    if path is None:
        path = Settings.documents.path_to_md_cleaned
    
    texts = load_text(path)
    texts = merge_text(texts)

    headers_to_split_on = [
        ("#", "Article"),
        ("##", "Paragraph"),
        ("###", "Subparagraph")
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on = headers_to_split_on,
        return_each_line = True
    )
    md_header_splits = markdown_splitter.split_text(texts)

    if codex_name is None:
        codex_name = Settings.data.name
    
    md_header_splits = set_metadata_to_documents(
        param_name = "Codex",
        param_value = codex_name,
        docs = md_header_splits
    )

    return md_header_splits


def md_parser():
    preprocessing()
    # md_split = document_split()


if __name__ == "__main__":
    md_parser()