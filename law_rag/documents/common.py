"""
Some usual functions for interaction with documents, like save, load, merge, etc.
"""

from langchain_core.documents import Document
from typing import List, Union

def load_text(path: str) -> List[str]:
    """Load text from the file
    
    Arguments
    ---------
    path: str
        Path to the file
    
    Returns
    -------
    texts: List[str]
        Text from the file    
    """
    with open(
        file = path,
        mode = "r",
        encoding = "utf-8"
    ) as file:
        texts = file.readlines()
    
    return texts

def save_text(texts: List[str], save_path: str) -> None:
    """Save text to the file
    
    Arguments
    ---------
    texts: List[str]
        Texts that need to save
    save_path: str
        Path to the file (include file extension)
    """
    with open(
        file = save_path,
        mode = "w+t",
        encoding = "utf-8"
    ) as file:
        file.writelines(texts)

def merge_text(texts: List[str]) -> str:
    """Merge text from the List of String to very one String
    
    Arguments
    ---------
    texts: List[str]
        Texts that need to save
    
    Returns
    -------
    full_text: str
        Text in very one String
    """
    full_text = "".join(texts)
    return full_text

def set_metadata_to_documents(
    param_name: str, 
    param_value: Union[int, float, str], 
    docs: List[Document]
) -> List[Document]:
    """Set the one specific metadata to all Documents
    
    This function is used for setting a metadata parameter to all Documents in List.

    For example, if the Document contains this pack of metadata:
    ```
    {"source": "path_to_source_document", "number": 45}
    ```
    
    after `set_metadata_to_documents` call:
    ```python
    from langchain_core.documents import Document

    docs: List[Documents]
    docs = set_metadata_to_documents(
        param_name: "new",
        param_value: "value",
        docs = docs
    )
    ``` 
    
    the Document metadata (for all Documents in List) will contain the new parameter. Like this:
    ```
    {"source": "path_to_source_document", "number": 45, "new": "value"}
    ```


    Arguments
    ---------
    param_name: str
        Name of the new metadata parameter
    param_value: Union[int, float, str]
        Value of the new metadata parameter
    docs: List[Document]
        List of Documents that needs new metadata parameter
        
    Returns
    -------
    docs: List[Documents]
        List of Documents with new metadata parameter
    """
    for doc in docs:
        doc.metadata[param_name] = param_value
    return docs