# This Embeddings Wrapper Class was taken from this source:
# https://github.com/langchain-ai/langchain/issues/15729
# to use Huggingface Embeddings Model with Neo4j Vector Store

from langchain_core.embeddings import Embeddings
from transformers import AutoTokenizer, AutoModel

from law_rag.config import Settings

from typing import List


class HuggingFaceEmbeddings(Embeddings):
    def __init__(self, model_name: str) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def embed_query(self, text: str) -> List[float]:
        inputs = self.tokenizer(text, return_tensors = 'pt', truncation = True)
        outputs = self.model(**inputs)
        return outputs.last_hidden_state.sum(dim = 1)[0].detach().numpy().tolist()
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        answers = []
        for text in texts:
            answers.append(self.embed_query(text))
        return answers


def get_embeddings():
    embeddings = HuggingFaceEmbeddings(Settings.models.embeddings_model)
    return embeddings