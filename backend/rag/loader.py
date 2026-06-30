from langchain_community.document_loaders import (
    TextLoader,
    PyMuPDFLoader,
    Docx2txtLoader,
)


def load_pdf(file_path):
    loader = PyMuPDFLoader(file_path)
    return loader.load()



def load_text(file_path):
    loader = TextLoader(file_path, encoding="utf-8")
    return loader.load()



def load_docx(file_path):
    loader = Docx2txtLoader(file_path)
    return loader.load()



def load_documents(file_path):

    if file_path.endswith(".txt"):
        return load_text(file_path)

    elif file_path.endswith(".pdf"):
        return load_pdf(file_path)

    elif file_path.endswith(".docx"):
        return load_docx(file_path)

    else:
        raise ValueError("Unsupported file type")
