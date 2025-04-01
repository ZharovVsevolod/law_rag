"""
Some functions for converting documents from one extension to another, like from pdf to markdown.

If you run this python file, it will convert pdf file, specified in the config file, to markdown, and save it in path, specified in the config file.
"""

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.output import text_from_rendered

from law_rag.config import Settings
from law_rag.documents.common import save_text

from typing import Optional

def pdf_to_markdown_convertion(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None
) -> None:
    """Convert pdf file to markdown format via Marker
    
    This function will convert pdf file to markdown and save it to another file. 
    
    You can specify the input and/or output paths.
    If you don't, the function will get it from the config file.

    Arguments
    ---------
    input_path: Optional[str] = None
        Path to the pdf file. If it is not specified, path will be pulled from the config file.
    output_path: Optional[str] = None
        Path where converted markdown file will be saved.  
        If it is not specified, path will be pulled from the config file.
    """
    # If paths are not set manually - we get them from the Settings module (config file)
    if input_path is None:
        input_path = Settings.documents.path_to_pdf
    if output_path is None:
        output_path = Settings.documents.path_to_md

    config = {
        "output_format": "markdown",
        "languages": "ru"
    }
    config_parser = ConfigParser(config)

    converter = PdfConverter(
        config = config_parser.generate_config_dict(),
        artifact_dict = create_model_dict(),
        processor_list = config_parser.get_processors(),
        renderer = config_parser.get_renderer(),
        llm_service = config_parser.get_llm_service()
    )

    rendered = converter(input_path)
    text, _, _ = text_from_rendered(rendered) # text, metadata, images

    # Save the markdown text to file
    save_text(
        texts = text, 
        save_path = output_path
    )


if __name__ == "__main__":
    pdf_to_markdown_convertion()