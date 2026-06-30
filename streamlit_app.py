import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="RAG Chat",
    # page_icon="💎",
    layout="wide"
)

# =========================
# LOAD CHAT HISTORY
# =========================

if "messages" not in st.session_state:

    try:

        response = requests.get(
            f"{API_URL}/chat"
        )

        st.session_state.messages = response.json()[
            "messages"
        ]

    except:

        st.session_state.messages = []

# =========================
# UPLOAD STATE
# =========================

if "last_uploaded_file" not in st.session_state:

    st.session_state.last_uploaded_file = None

# =========================
# LOAD FILES
# =========================

try:

    files_response = requests.get(
        f"{API_URL}/files"
    )

    uploaded_files = files_response.json()

except:

    uploaded_files = []

# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.title("RAG-BASED Personal Chat")

    st.markdown("---")

    st.subheader("Upload File")

    uploaded_file = st.file_uploader(
        "Upload",
        type=["txt", "pdf", "docx"],
        label_visibility="collapsed"
    )

    # =========================
    # SAFE UPLOAD
    # =========================

    if uploaded_file:

        # prevent infinite upload loop
        if (
            st.session_state.last_uploaded_file
            != uploaded_file.name
        ):

            st.session_state.last_uploaded_file = (
                uploaded_file.name
            )

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue()
                )
            }

            with st.spinner(
                "Processing document..."
            ):

                response = requests.post(
                    f"{API_URL}/upload",
                    files=files
                )

            st.success(
                response.json()["message"]
            )

            st.rerun()

    # =========================
    # FILE LIST
    # =========================

    st.markdown("### Uploaded Files")

    for file in uploaded_files:

        st.markdown(
            f"""
            <div style="
                padding:12px;
                border-radius:12px;
                background:#1e1e2f;
                border:1px solid #2d2d44;
                margin-bottom:10px;
                color:white;
                font-size:15px;
                font-weight:500;
                display:flex;
                align-items:center;
                gap:10px;
            ">
                📄 <span>{file['name']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # =========================
    # SLASH COMMAND HELP
    # =========================

    st.markdown(
        """
        ### Slash Commands
        
        Type:
        
        `/filename`
        
        Example:
        
        `/google.txt`
        """
    )

    with st.expander("Available Commands"):

        for file in uploaded_files:

            st.code(f"/{file['name']}")

    st.markdown("---")

    # =========================
    # CLEAR CHAT
    # =========================

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        requests.delete(
            f"{API_URL}/chat"
        )

        st.session_state.messages = []

        st.rerun()

# =========================
# TITLE
# =========================

if len(st.session_state.messages) == 0:

    st.markdown(
        """
        <h1 style='text-align:center; margin-top:120px;'>
            Ask your documents anything
        </h1>

        <p style='text-align:center; color:gray;'>
            Upload a file in the sidebar, then start a conversation.
        </p>
        """,
        unsafe_allow_html=True
    )

# =========================
# CHAT HISTORY
# =========================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(
            msg["content"],
            unsafe_allow_html=True
        )

# =========================
# CHAT INPUT
# =========================

prompt = st.chat_input(
    "Ask something..."
)

if prompt:

    # =========================
    # USER MESSAGE
    # =========================

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):

        st.markdown(prompt)

    # =========================
    # FILE SUMMARY MODE
    # =========================

    if prompt.startswith("/"):

        filename = prompt[1:].strip()

        with st.chat_message("assistant"):

            with st.spinner(
                "Analyzing document..."
            ):

                response = requests.post(
                    f"{API_URL}/summarize-file",
                    json={
                        "filename": filename
                    }
                )

                answer = response.json()[
                    "summary"
                ]

                st.markdown(
                    answer,
                    unsafe_allow_html=True
                )

    # =========================
    # NORMAL CHAT MODE
    # =========================

    else:

        with st.chat_message("assistant"):

            with st.spinner(
                "Thinking..."
            ):

                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "user_query": prompt
                    }
                )

                answer = response.json()[
                    "answer"
                ]

                st.markdown(
                    answer,
                    unsafe_allow_html=True
                )

    # =========================
    # SAVE ASSISTANT MESSAGE
    # =========================

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })