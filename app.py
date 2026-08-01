import streamlit as st

from database import read_chunks_from_database
from main import find_top_chunks_with_saved_embeddings
from foundry_answer import (
    generate_foundry_answer,
    generate_foundry_summary,
    generate_foundry_quiz,
    generate_foundry_flashcards
)


st.set_page_config(
    page_title="Local RAG Study Assistant",
    page_icon="📚",
    layout="centered"
)


st.title("📚 Local RAG Study Assistant")

st.write(
    "Ask questions and create study materials from your local notes "
    "with Microsoft Foundry Local."
)

st.caption(
    "Semantic vector search • Local AI • SQLite • Source-grounded answers"
)


with st.sidebar:
    st.header("About")

    st.write(
        "This assistant retrieves relevant information from local "
        "study documents and uses an on-device model to generate a response."
    )

    st.subheader("Models")

    st.write("**Embedding:** qwen3-embedding-0.6b")
    st.write("**Chat:** qwen2.5-0.5b")

    st.subheader("Retrieval")

    st.write("Top-k chunks: 2")
    st.write("Minimum relevance score: 0.35")


mode = st.selectbox(
    "Study mode",
    [
        "Ask",
        "Summarize",
        "Quiz",
        "Flashcards"
    ]
)


request_text = st.text_area(
    "Question or topic",
    placeholder="Example: What is RAG?",
    height=120
)


generate_button = st.button(
    "Generate",
    type="primary",
    use_container_width=True
)


if generate_button:
    clean_request = request_text.strip()

    if not clean_request:
        st.warning("Please write a question or topic.")

    else:
        with st.spinner(
            "Searching local documents and generating your result..."
        ):
            try:
                chunks = read_chunks_from_database()

                relevant_chunks = (
                    find_top_chunks_with_saved_embeddings(
                        clean_request,
                        chunks
                    )
                )

                if mode == "Ask":
                    result = generate_foundry_answer(
                        clean_request,
                        relevant_chunks
                    )

                elif mode == "Summarize":
                    result = generate_foundry_summary(
                        clean_request,
                        relevant_chunks
                    )

                elif mode == "Quiz":
                    result = generate_foundry_quiz(
                        clean_request,
                        relevant_chunks
                    )

                else:
                    result = generate_foundry_flashcards(
                        clean_request,
                        relevant_chunks
                    )

                st.subheader("Result")
                st.text(result.strip())

            except Exception as error:
                st.error(
                    "The assistant could not generate a result."
                )

                with st.expander("Technical details"):
                    st.exception(error)