"""
Some functions for converting documents from one extension to another, like from pdf to markdown.

If you run this python file, it will convert pdf file, specified in the config file, to markdown, and save it in path, specified in the config file.
"""
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.output import text_from_rendered

from law_rag.config import Settings
from law_rag.documents.common import save_text, list_files_in_foler

def pdf_to_markdown_convertion(
    input_path: str,
    output_path: str
) -> None:
    """Convert pdf file to markdown format via Marker
    
    This function will convert pdf file to markdown and save it to another file. 
    
    You can specify the input and/or output paths.
    If you don't, the function will get it from the config file.

    Arguments
    ---------
    input_path: str
        Path to the pdf file
    output_path: str
        Path where converted markdown file will be saved
    """
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

def convert_all() -> None:
    codexes = list_files_in_foler(Settings.documents.path_to_folder)

    for codex in codexes:
        pdf_to_markdown_convertion(
            input_path = Settings.documents.pdf(codex),
            output_path = Settings.documents.md(codex)
        )


if __name__ == "__main__":
    convert_all()