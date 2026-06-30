from backend.rag.loader import load_documents
from backend.utils import get_vectordb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langsmith import traceable


splitter = RecursiveCharacterTextSplitter(
    chunk_size=850,
    chunk_overlap=150
)

vectordb = get_vectordb()

@traceable(name="ingest_documents", run_type="tool")
def ingest_single_file(file_path):

    documents = load_documents(file_path)

    chunks = splitter.split_documents(documents)

    vectordb.add_documents(chunks)

    print(f"Inserted {len(chunks)} chunks")

