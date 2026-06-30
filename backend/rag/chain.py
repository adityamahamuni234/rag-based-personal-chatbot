from backend.utils import get_llm
from backend.rag.retriever import history_aware_retriever
from backend.rag.prompts import qa_prompt
from backend.rag.history import get_chat_history

from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain
)

from langchain_classic.chains.retrieval import (
    create_retrieval_chain
)

from langchain_core.runnables.history import (
    RunnableWithMessageHistory
)

llm = get_llm()

question_answer_chain = create_stuff_documents_chain(
    llm,
    qa_prompt
)

rag_chain = create_retrieval_chain(
    history_aware_retriever,
    question_answer_chain
)

conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_chat_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)