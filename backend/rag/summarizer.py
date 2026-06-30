from pathlib import Path
from langsmith import traceable
from backend.utils import get_llm
from backend.rag.prompts import summary_prompt

# =========================
# LLM
# =========================

llm = get_llm()

# =========================
# SUMMARY STORAGE
# =========================

SUMMARY_DIR = Path(
    "backend/rag/summaries"
)

SUMMARY_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =========================
# CONFIG
# =========================

# Safe for ~8k context window
MAX_DOCUMENT_CHARS = 25000

# =========================
# PATH HELPERS
# =========================

def get_summary_path(
    filename: str
):

    stem = Path(filename).stem

    return SUMMARY_DIR / f"{stem}.md"


def load_summary(
    filename: str
):

    summary_path = get_summary_path(
        filename
    )

    if summary_path.exists():

        return summary_path.read_text(
            encoding="utf-8"
        )

    return None


def save_summary(
    filename: str,
    content: str
):

    summary_path = get_summary_path(
        filename
    )

    summary_path.write_text(
        content,
        encoding="utf-8"
    )

# =========================
# MAIN SUMMARY FUNCTION
# =========================

@traceable(name="generate_summary", run_type="chain")
async def generate_summary(
    filename: str,
    documents
):

    # =========================
    # RETURN CACHED SUMMARY
    # =========================

    existing = load_summary(
        filename
    )

    if existing:

        return existing

    # =========================
    # EXTRACT FULL TEXT
    # =========================

    full_text = "\n\n".join([

        doc.page_content

        for doc in documents

        if getattr(
            doc,
            "page_content",
            None
        )

    ]).strip()

    # =========================
    # EMPTY DOCUMENT
    # =========================

    if not full_text:

        return (
            "# Table of Contents\n\n"
            "- No readable content found."
        )

    # =========================
    # LIMIT DOCUMENT SIZE
    # =========================

    full_text = (
        full_text[:MAX_DOCUMENT_CHARS]
        .rsplit(" ", 1)[0]
    )

    # =========================
    # GENERATE SUMMARY
    # =========================

    response = await llm.ainvoke(

        summary_prompt.format_messages(

            document=full_text

        )

    )

    summary = response.content.strip()

    # =========================
    # FALLBACK
    # =========================

    if not summary:

        summary = (
            "# Table of Contents\n\n"
            "- Could not generate summary."
        )

    # =========================
    # SAVE SUMMARY
    # =========================

    save_summary(

        filename,
        summary

    )

    return summary