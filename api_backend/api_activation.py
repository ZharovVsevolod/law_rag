import ast
import logging

import uvicorn

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from law_rag.knowledge.db_connection import langchain_neo4j_vector
from law_rag.models.llm_wrapper import (
    get_llm_model, 
    get_runnable_chain, 
    make_config_for_chain,
    retriever_answer
)
from law_rag.db_manager.data_management import generate_hex
from law_rag.config import Settings

from dotenv import load_dotenv

app = FastAPI()

#------------------------
# React could connect to FastApi WebSocket if some ports will be open along with CORS
# https://fastapi.tiangolo.com/tutorial/cors/#use-corsmiddleware
#------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -----------------------


@app.get("/")
def read_root():
    """Check connection"""
    return {"message": "Wake up, Neo"}


@app.websocket("/ws/chat/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    model = get_llm_model(
        model_type = Settings.models.llm_model_type,
        engine = Settings.models.llm_engine,
        inside_docker_container = False
    )
    
    vector_graph_naive = langchain_neo4j_vector("naive")
    vector_graph_holmes = langchain_neo4j_vector("holmes")

    runnable_with_history = get_runnable_chain(model)
    session_id = generate_hex()
    config = make_config_for_chain(session_id)

    while True:
        data = await websocket.receive_text()
        message = ast.literal_eval(data)["message"]

        # RAG system
        match Settings.web.mode:
            case "all":
                retriever_message_naive, raw_retriever_message_naive = retriever_answer(
                    question = message,
                    retriever = vector_graph_naive,
                    return_also_raw_answer = True
                )
                retriever_message_holmes, raw_retriever_message_holmes = retriever_answer(
                    question = message,
                    retriever = vector_graph_holmes,
                    return_also_raw_answer = True,
                    ship_headers = True
                )
                retriever_message = retriever_message_naive + "\n\n" + retriever_message_holmes
                raw_retriever_message = raw_retriever_message_naive + "\n\n### Триплеты\n" + raw_retriever_message_holmes
            
            case "naive":
                retriever_message, raw_retriever_message = retriever_answer(
                    question = message,
                    retriever = vector_graph_naive,
                    return_also_raw_answer = True
                )

            case "holmes":
                retriever_message, raw_retriever_message = retriever_answer(
                    question = message,
                    retriever = vector_graph_holmes,
                    return_also_raw_answer = True,
                    ship_headers = True
                )

        if Settings.web.need_to_show_rag:
            await websocket.send_json({
                "event": "rag_system",
                "name": "RAG",
                "data": raw_retriever_message,
                "run_id": "rag_system"
            })

        async for chunk in runnable_with_history.astream_events({'input': retriever_message}, version="v2", config=config):
            if chunk["event"] in ["on_parser_start", "on_parser_stream"]:
                await websocket.send_json(chunk)



if __name__ == "__main__":
    load_dotenv()

    # API application
    uvicorn.run(
        app = app, 
        host = Settings.api.host, 
        port = Settings.api.port
    )