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
    set_metadata_to_documents,
    list_files_in_foler
)

from typing import List, Optional, Tuple

import logging
logger = logging.getLogger(__name__)

def find_all_markdown_links(
    md_text: str,
    return_cleaned_text: bool = Settings.data.clean_text_from_links,
    placeholder: Optional[str] = None
) -> List[Tuple[str, str]] | Tuple[List[Tuple[str, str]], str]:
    """Find and return all links in markdown text. Optionally return text without any links (they will be replaced with a placeholder).

    This function will find all links (and text that linked with them) that appear in the provided markdown text. They will be returned as a tuple of 
    - some text that was referenced to link
    - the link

    Example 1
    ---------
    For example, if we have this text:
    ```markdown
    Some [text](www.text.com) that we have like an [example](www.example.com) here.
    ```
    
    after this function call
    ```pythonreturn_cleaned_text
    ```

    if will return this:
    ```python
    links: List = [
        "text", "www.text.com",
        "example", "www.example.com"
    ]
    ```

    Example 2
    ---------
    Also you can modify the text with some placeholder in place.
    ```python
    text = load_markdown_text()
    links, new_text = find_all_markdown_links(
        text,
        return_cleaned_text = True,
        placeholder = "This link was deleted"
    )
    ```

    if will return this `new_text`:
    ```markdown
    Some [text](This link was deleted) that we have like an [example](This link was deleted) here.
    ```

    Arguments
    ---------
    md_text: str
        Some markdown text that need to be modified
    return_cleaned_text: bool = False
        If need to return the cleaned text too. Default is *False*
    placeholder: Optional[str] = None
        If required, what we need to put in place of deleted link.  
        If it is *None* and `return_cleaned_text` is *True*, the placeholder will be got from the config file
    
    Returns
    -------
    links: List[Tuple[str, str]]
        The list of links that was found in the markdown text
    cleaned_md_text: Optional[str]
        The markdown text that was cleaned from the links
    """
    # Some magic formula. I have got this one from this source:
    # https://stackoverflow.com/questions/63197371/detecting-all-links-in-markdown-files-in-python-and-replace-them-with-outputs-of
    INLINE_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    links = list(INLINE_LINK_RE.findall(md_text))

    if return_cleaned_text:
        just_links = []
        for _, link in links:
            just_links.append(link)

        if placeholder is None:
            placeholder = Settings.data.link_placeholder

        cleaned_md_text = remove_links_from_text(md_text, just_links, placeholder)
        return links, cleaned_md_text

    return links

def remove_links_from_text(
    md_text: str,
    links: List[str]| str,
    placeholder: str
) -> str:
    """Remove provided links from the text in the Markdown markup
    
    This function will remove the links and will replce them with given placeholder.
    
    Example 1
    -------
    For example, if we have this text:
    ```markdown
    Some [text](www.text.com) that we have like an [example](www.example.com) here.
    ```

    we can use this function to replace the exact same link as provided to placeholder:
    ```python
    text = load_markdown_text()

    new_text = remove_links_from_text(
        md_text = text,
        links = ["www.example.com"],
        placeholder = "This link was deleted"
    )
    ```

    so the result will be:
    ```markdown
    Some [text](www.text.com) that we have like an [example](This link was deleted) here.
    ```

    Example 2
    -------
    You could give a single link that need to be removed (like in an example) or a list of links
    ```python
    text = load_markdown_text()

    new_text = remove_links_from_text(
        md_text = text,
        links = ["www.example.com", "www.text.com"],
        placeholder = "This link was deleted"
    )
    ```
    
    and the result will be like this as well:
    ```markdown
    Some [text](This link was deleted) that we have like an [example](This link was deleted) here.
    ```

    Arguments
    ---------
    md_text: str
        Some markdown text that need to be modified
    links: List[str]| str
        Some links that need to be deleted from the text
    placeholder: str
        What we need to put in place of deleted link
    
    Returns
    -------
    md_text_without_links: str
        Markdown text without links
    """
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

def rus_character_to_digit(character: str, skip_some_characters: bool = True) -> int:
    """Transform the Russian characters to serial number
    
    - а -> 1
    - б -> 2
    - в -> 3
    - г -> 4
    - д -> 5

    etc.

    Also sometimes characters like ё or й are *not* skipped in serial order. For this variant set parameter `skip_some_characters` to False.

    Arguments
    ---------
    character: str
        The character that is need to transform to serial number
    skip_some_characters: bool = True
        Extra boolean parameter to skip or not to skip some of the Russian characters that may be skipped in the original document.  
        Default is *True* - to skip.
    
    Returns
    -------
    number: int
        The serial number of Russian character
    """
    number = ord(character) - 1071 # because the russian "а" character is 1072

    if skip_some_characters:
        # the й character - 11th
        if number > 10:
            number -= 1
    
    else:
        # the ё character - 7th
        if number > 6:
            number += 1
        if number == 35:
            number = 7

    return number

def make_headers_for_article(texts: List[str]) -> List[str]:
    """Make new custom headers in the markdown texts of Russian Codex
    
    That function is setting programly up new headers in the markdown text based on:
    - The **Header 1** (`#`) is set for keyword "Статья" in the text (the article name will be in the header text)
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
                            part = digit[:-1]
                            # They can also be like а), б), в), г), etc.
                            if not part.isdigit():
                                part = rus_character_to_digit(part, skip_some_characters = True)
                            
                            texts[i] = f"### Подпункт {part}\n" + text
            
            except Exception as e:
                pass
        
    return texts

def change_quotes(texts: List[str]) -> List[str]:
    """Replace double quotes (") for single (')

    That is necessary because Neo4j uses double quotes for strings, so it need to be signle for proper work.
    
    Arguments
    ---------
    texts: List[str]
        List of Markdown text that may content double quotes
    
    Returns
    -------
    texts: List[str]
        List of Markdown text with only single quotes
    """
    for i, text in enumerate(texts):
        texts[i] = text.replace('"', "'")
    
    return texts

def preprocessing(
    input_path: str,
    output_path: str
) -> None:
    """Preprocess markdown text
    
    It includes:
    - Clean any headers from the text
    - Set up new custom headers

    You can specify the input and/or output paths.
    If you don't, the function will get it from the config file.

    Arguments
    ---------
    input_path: str
        Path to the pdf file
    output_path: str
        Path where converted markdown file will be saved
    """    
    texts = load_text(input_path)
    logger.info("The file was loaded")

    texts = clean_headers(texts)
    logger.info("The headers was removed")

    texts = make_headers_for_article(texts)
    logger.info("The headers was created")

    save_text(texts, output_path)
    logger.info("The file was saved")


def fix_automatization_parsing_mistakes(chunks: List[Document]) -> List[Document]:
    # Subparagraphs without Paragraphs - promote in rank
    for chunk in chunks:
        if ("Subparagraph" in chunk.metadata) and ("Paragraph" not in chunk.metadata):
            chunk.metadata["Paragraph"] = chunk.metadata["Subparagraph"]
            del chunk.metadata["Subparagraph"]
    
    # Unite chunks
    n = len(chunks)
    for i in range(n - 1):
        try:
            if chunks[i].metadata == chunks[i + 1].metadata:
                chunks[i].page_content = chunks[i].page_content + "\n" + chunks[i + 1].page_content
                del chunks[i + 1]
                i = i - 1
        except IndexError:
            break

    return chunks


def document_split(
    codex_name: str,
    path: Optional[str] = None
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
    - The source name (Should be a number like "149")

    Arguments
    ---------
    codex_name: str
        The source name that will be set for "Codex" name in matadata.  
        It'll be also used for path if path is not specified
    path: Optional[str] = None
        Path to markdown text. If it is not specified, path will be pulled from the config file.
    
    Returns
    -------
    markdown_text_header_split: List[Document]
        The splitted by headers markdown text
    """
    if path is None:
        path = Settings.documents.md_clean(codex_name)
    
    texts = load_text(path)

    # Change double quotes for single for Neo4j
    texts = change_quotes(texts)

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
    
    md_header_splits = set_metadata_to_documents(
        param_name = "Codex",
        param_value = codex_name,
        docs = md_header_splits
    )

    # Fix some mistakes that occures in preprocessing
    md_header_splits = fix_automatization_parsing_mistakes(md_header_splits)

    return md_header_splits

def preprocess_all_md_files() -> None:
    codexes = list_files_in_foler(Settings.documents.path_to_folder)

    for codex in codexes:
        preprocessing(
            input_path = Settings.documents.md(codex),
            output_path = Settings.documents.md_clean(codex)
        )


if __name__ == "__main__":
    preprocess_all_md_files()