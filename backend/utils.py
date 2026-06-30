from langchain_openai import OpenAIEmbeddings
from langchain_groq import ChatGroq
from langchain_weaviate import WeaviateVectorStore
from dotenv import load_dotenv
import weaviate
import os

load_dotenv()

_embedding_model = None
_vectordb = None
_llm = None
_weaviate_client = None
_llm2 = None


# =========================
# EMBEDDINGS
# =========================

def get_embedding_model():

    global _embedding_model

    if _embedding_model is None:
        _embedding_model = OpenAIEmbeddings(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="text-embedding-3-small"
        )
    return _embedding_model


# =========================
# WEAVIATE CLIENT
# =========================

# =========================
# WEAVIATE CLIENT
# =========================

def get_weaviate_client():

    global _weaviate_client

    if _weaviate_client is None:

        _weaviate_client = weaviate.connect_to_local(
            host="localhost",
            port=8080
        )

    return _weaviate_client


# =========================
# VECTOR DB
# =========================

def get_vectordb():

    global _vectordb

    if _vectordb is None:

        client = get_weaviate_client()

        # =========================
        # CREATE COLLECTION IF MISSING
        # =========================

        if not client.collections.exists(
            "RAGDocuments"
        ):

            client.collections.create(
                name="RAGDocuments"
            )

        _vectordb = WeaviateVectorStore(

            client=client,

            index_name="RAGDocuments",

            text_key="page_content",

            embedding=get_embedding_model()

        )

    return _vectordb

# =========================
# LLM
# =========================

def get_llm():

    global _llm

    if _llm is None:
        _llm = ChatGroq(
            model="openai/gpt-oss-120b",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.1
        )
    return _llm
