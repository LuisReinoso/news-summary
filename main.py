from langchain_community.document_loaders.youtube import YoutubeLoader, TranscriptFormat
from langchain_community.chat_models import ChatOllama
from langchain_community.chat_models import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import os
my_key_news_summary = os.getenv("MY_KEY_NEWS_SUMMARY")
groq_key = os.getenv("GROQ_API_KEY")

origins = [
    "https://luisreinoso.dev",
    "http://localhost:4200",
]


class Item(BaseModel):
    youtubeUrl: str | None = None
    key: str | None = None


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def summary_video(url):
    # chatModel = ChatOllama(model="internlm2")
    # chatModel = ChatOpenAI(model="gpt-3.5-turbo")
    chatModel = ChatGroq(model_name="mixtral-8x7b-32768", api_key=groq_key)
    videoLoader = YoutubeLoader.from_youtube_url(url)
    videoLoader.language = ['es']
    videoLoader.transcript_format = TranscriptFormat.CHUNKS
    documents = videoLoader.load()

    response = []

    for document in documents:
        chat = chatModel(messages=[
            SystemMessage(content="Resumen cada tema descrito en el texto de las noticias, muestra SOLO el resumen en una oracion de MAXIMO 100 caracteres, es obligatorio no pasar de 100 caracteres"),
            HumanMessage(
                content=f"Noticias: {document}")])
        response.append(
            {"summary": chat.content, "source": document.metadata})

    return response


@app.options("/news-summary")
async def options_news_summary():
    return {"data": "ok"}


@app.post("/news-summary")
async def analyze_video(item: Item):

    print("key", item.key)
    print("value", my_key_news_summary)

    if item.key != my_key_news_summary:
        raise HTTPException(status_code=404, detail="Invalid key")

    response = summary_video(url=item.youtubeUrl)
    return {"data": response}


@app.get("/")
async def root():
    return {"data": "ok"}
