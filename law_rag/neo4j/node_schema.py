from pydantic import BaseModel
from typing import List, Tuple

class Node(BaseModel):
    number: str
    previous: str
    parents: List[str]

    @property
    def type(self):
        return "BaseNode"

    def primal_key(self) -> Tuple[str, str]:
        return "number", self.number

    def all_parameters(self) -> set[str]:
        return self.model_fields_set
    
    def system_parameters(self) -> List[str]:
        return ["previous", "parents"]

# -----

class Codex(Node):
    name: str

    @property
    def type(self):
        return "Codex"


class Article(Node):
    name: str

    @property
    def type(self):
        return "Article"


class Paragraph(Node):
    text: str
    has_reference: bool
    references: List[Tuple[str, str]]

    @property
    def type(self):
        return "Paragraph"


class Subparagraph(Node):
    text: str
    has_reference: bool
    references: List[Tuple[str, str]]

    @property
    def type(self):
        return "Subparagraph"
