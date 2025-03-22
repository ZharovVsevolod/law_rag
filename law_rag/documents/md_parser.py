from langchain_text_splitters import MarkdownHeaderTextSplitter

from law_rag.config import Settings
from law_rag.documents.common import load_text, save_text

from typing import List

import logging
logger = logging.getLogger(__name__)


def clean_headers(texts: List[str]) -> List[str]:
    for i, text in enumerate(texts):
        if "#" in text:
            texts[i] = text.replace("#", "")
    
    return texts

def make_headers_for_article(texts: List[str]) -> List[str]:
    for i, text in enumerate(texts):
        if "Статья" in text:
            texts[i] = "#" + text
    
    return texts

def preprocessing() -> None:
    texts = load_text(Settings.documents.path_to_md)
    logger.info("The file was loaded")

    texts = clean_headers(texts)
    logger.info("The headers was removed")

    texts = make_headers_for_article(texts)
    logger.info("The headers was created")

    save_text(texts, Settings.documents.path_to_md_cleaned)
    logger.info("The file was saved")

def merge_text(texts: List[str]) -> str:
    full_text = "".join(texts)
    return full_text

def document_split() -> List[str]:
    texts = load_text(Settings.documents.path_to_md_cleaned)
    texts = merge_text(texts)

    headers_to_split_on = [
        ("#", "Header_1")
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
    md_header_splits=  markdown_splitter.split_text(texts)

    return md_header_splits


def md_parser():
    preprocessing()
    md_split = document_split()


if __name__ == "__main__":
    md_parser()