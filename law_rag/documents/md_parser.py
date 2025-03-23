from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document

from law_rag.config import Settings
from law_rag.documents.common import (
    load_text, 
    save_text, 
    merge_text, 
    set_metadata_to_documents
)

from typing import List, Optional

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

def preprocessing() -> None:
    texts = load_text(Settings.documents.path_to_md)
    logger.info("The file was loaded")

    texts = clean_headers(texts)
    logger.info("The headers was removed")

    texts = make_headers_for_article(texts)
    logger.info("The headers was created")

    save_text(texts, Settings.documents.path_to_md_cleaned)
    logger.info("The file was saved")

def document_split(
        path: Optional[str] = None,
        codex_name: Optional[str] = None
    ) -> List[Document]:
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