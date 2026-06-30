from backend.utils import get_vectordb, get_llm 
from langchain_classic.chains import create_history_aware_retriever
from backend.rag.prompts import contextualize_q_prompt
from langchain_core.runnables import RunnableLambda
from langsmith import traceable


db = get_vectordb()
llm = get_llm()

# =========================
# HYBRID SEARCH
# =========================

@traceable(name="hybrid_search", run_type="retriever")
def hybrid_search(query: str):

    docs = db.similarity_search(query=query,k=6,alpha=0.5)
    return docs

# =========================
# CUSTOM RETRIEVER
# =========================

base_retriever = RunnableLambda(lambda query: hybrid_search(query))

# =========================
# HISTORY AWARE RETRIEVER
# =========================

print("LLM:", llm)
print("Retriever:", base_retriever)
print("Prompt:", contextualize_q_prompt)

history_aware_retriever = (
    create_history_aware_retriever(
        llm=llm,
        retriever=base_retriever,
        prompt=contextualize_q_prompt
    )
)