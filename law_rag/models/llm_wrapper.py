from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_neo4j import Neo4jVector

from law_rag.db_manager.data_management import get_session_history_with_local_file
from law_rag.models.blanks import (
    SYSTEM_PROMPT, 
    add_retirver_answer_to_question, 
    transform_answer_list
)
from law_rag.config import Settings

from typing import Literal, Tuple

def get_llm_model(
    model_type: Literal["qwen3:8b", "deepseek-r1:8b", "gemma3:4b", "gemma2"],
    engine: Literal["ollama"] = "ollama"
) -> ChatOllama:
    """Get an LLM model"""
    match engine:
        case "ollama":
            llm = ChatOllama(
                model = model_type,
                # base_url = Settings.models.llm_base_url
            )
    
    return llm


def retriever_answer(
        question: str, 
        retriever: Neo4jVector,
        return_also_raw_answer: bool = False
    ) -> str | Tuple[str, str]:
    """Get an answer from Retriever"""
    answer_nodes = retriever.similarity_search(
        query = question,
        k = 3
    )
    answer_nodes = [node.page_content for node in answer_nodes]

    answer = add_retirver_answer_to_question(question, answer_nodes)

    if return_also_raw_answer:
        raw_answer = transform_answer_list(answer_nodes)
        return answer, raw_answer

    return answer


def get_runnable_chain(model):
    """Call format:\n
    - With Streaming:\n
    ```python
        async for chunk in runnable_chain.astream_events(
            {'input': user_message}, version="v2", config=config
        ):
            if chunk["event"] in ["on_parser_start", "on_parser_stream"]:
                print(chunk)
    ```

    - Without Streaming
    ``` python
        runnable_chain.invoke({'input': user_message}, version="v2", config=config)
    ```
    
    config could be created from `make_config_for_chain` function
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT.content),
        ("placeholder", "{history}"),
        ("user", "{input}")
    ])

    str_parser = StrOutputParser()
    chain = prompt | model | str_parser.with_config({"run_name": Settings.web.run_name})

    runnable_with_history = RunnableWithMessageHistory(
        runnable = chain,
        get_session_history = get_session_history_with_local_file,
        input_messages_key = "input",
        history_messages_key = "history"
    )

    return runnable_with_history


def make_config_for_chain(session_id: str) -> dict:
    """Config for runnable_chain"""
    return {"configurable": {"session_id": session_id}}
