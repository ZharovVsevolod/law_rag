from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.output import text_from_rendered

from law_rag.config import Settings
from law_rag.documents.common import save_text

def pdf_to_markdown_convertion() -> None:
    config = {
        "output_format": "markdown",
        "output_dir": Settings.documents.path_to_folder,
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

    rendered = converter(Settings.documents.path_to_pdf)
    text, _, _ = text_from_rendered(rendered) # text, metadata, images

    # Save the markdown text to file
    save_text(
        texts = text, 
        save_path = Settings.documents.path_to_md
    )


if __name__ == "__main__":
    pdf_to_markdown_convertion()