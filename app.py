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
    layout="wide"
)


def format_result_for_markdown(result):
    formatted_lines = []

    headings = {
        "Answer:": "## Answer",
        "Short answer:": "### Short answer",
        "Key points:": "### Key points",
        "Exam note:": "### Exam note",
        "Grounding note:": "### Grounding note",
        "Summary:": "## Summary",
        "Quiz:": "## Quiz",
        "Flashcards:": "## Flashcards",
        "Sources:": "### Retrieved sources"
    }

    for line in result.strip().splitlines():
        clean_line = line.strip()

        if not clean_line:
            formatted_lines.append("")
            continue

        if clean_line in headings:
            formatted_lines.append(headings[clean_line])

        elif clean_line.startswith("Question "):
            formatted_lines.append(f"**{clean_line}**")

        elif clean_line.startswith("Answer "):
            formatted_lines.append(clean_line)

        elif clean_line.startswith("Card "):
            formatted_lines.append(f"#### {clean_line}")

        elif clean_line.startswith("Q:"):
            formatted_lines.append(f"**{clean_line}**")

        elif clean_line.startswith("A:"):
            formatted_lines.append(clean_line)

        else:
            formatted_lines.append(clean_line)

    return "\n\n".join(formatted_lines)


st.markdown(
    """
    <style>
        .block-container {
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        div[data-testid="stMetric"] {
            background-color: rgba(120, 120, 120, 0.08);
            border: 1px solid rgba(120, 120, 120, 0.18);
            border-radius: 12px;
            padding: 14px;
        }

        div.stButton > button {
            border-radius: 10px;
            font-weight: 600;
        }

        div[data-testid="stTextArea"] textarea {
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("📚 Local RAG Study Assistant")

st.write(
    "Study from your own local notes with semantic vector search "
    "and on-device artificial intelligence."
)

st.caption(
    "Microsoft Foundry Local • SQLite • Top-k retrieval • Offline capable"
)


try:
    chunks = read_chunks_from_database()

except Exception as error:
    st.error("The local document database could not be opened.")

    with st.expander("Technical details"):
        st.exception(error)

    st.stop()


document_names = []

for chunk_id, filename, content, embedding in chunks:
    if filename not in document_names:
        document_names.append(filename)


metric_column1, metric_column2, metric_column3 = st.columns(3)

with metric_column1:
    st.metric("Documents", len(document_names))

with metric_column2:
    st.metric("Stored chunks", len(chunks))

with metric_column3:
    st.metric("Top-k retrieval", 2)


st.divider()


with st.sidebar:
    st.header("⚙️ System information")

    st.subheader("Local models")

    st.write("**Embedding model**")
    st.code("qwen3-embedding-0.6b", language=None)

    st.write("**Chat model**")
    st.code("qwen2.5-0.5b", language=None)

    st.subheader("Retrieval settings")

    st.write("Top-k chunks: **2**")
    st.write("Minimum relevance score: **0.35**")

    st.subheader("Available documents")

    for document_name in document_names:
        st.write(f"• {document_name}")

    st.divider()

    st.success(
        "The application can run locally after the models "
        "have been downloaded."
    )


mode_descriptions = {
    "Ask": "Answer a question using retrieved information.",
    "Summarize": "Create a concise summary of a topic.",
    "Quiz": "Generate questions and answers for revision.",
    "Flashcards": "Create quick question-and-answer cards."
}


with st.form("study_assistant_form"):
    mode = st.selectbox(
        "Study mode",
        [
            "Ask",
            "Summarize",
            "Quiz",
            "Flashcards"
        ]
    )

    st.caption(mode_descriptions[mode])

    request_text = st.text_area(
        "Question or topic",
        placeholder="Example: What is RAG?",
        height=130
    )

    generate_button = st.form_submit_button(
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
                relevant_chunks = (
                    find_top_chunks_with_saved_embeddings(
                        clean_request,
                        chunks
                    )
                )

                if not relevant_chunks:
                    st.info(
                        "I could not find relevant information "
                        "in the documents."
                    )

                else:
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

                    st.success(
                        f"{len(relevant_chunks)} relevant source "
                        "chunk(s) retrieved."
                    )

                    with st.container(border=True):
                        formatted_result = (
                            format_result_for_markdown(result)
                        )

                        st.markdown(formatted_result)

            except Exception as error:
                st.error(
                    "The assistant could not generate a result."
                )

                with st.expander("Technical details"):
                    st.exception(error)