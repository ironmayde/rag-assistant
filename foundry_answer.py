from foundry_local_sdk import Configuration, FoundryLocalManager
from foundry_local_sdk.exception import FoundryLocalException


_manager_initialized = False


def get_foundry_manager():
    global _manager_initialized

    if not _manager_initialized:
        config = Configuration(app_name="rag-assistant")

        try:
            FoundryLocalManager.initialize(config)
        except FoundryLocalException as error:
            if "singleton" not in str(error).lower():
                raise error

        _manager_initialized = True

    return FoundryLocalManager.instance


def generate_foundry_answer(question, best_chunk):
    if best_chunk is None:
        return "I could not find relevant information in the documents."

    chunk_id, filename, content, score = best_chunk

    manager = get_foundry_manager()
    model = manager.catalog.get_model("qwen2.5-0.5b")

    if not model.is_cached:
        model.download()

    model.load()
    client = model.get_chat_client()

    response = client.complete_chat([
        {
            "role": "system",
            "content": (
                "You are a local RAG study assistant. "
                "Answer the user's question only using the provided context. "
                "Do not use outside knowledge. "
                "Do not invent details. "
                "If the answer is not in the context, say: "
                "'I could not find this information in the document.' "
                "Write a clear and concise answer for a student."
            )
        },
        {
            "role": "user",
            "content": f"""
Context:
{content}

Question:
{question}
"""
        }
    ])

    short_answer = response.choices[0].message.content.strip()

    model.unload()

    return f"""
Answer:
Short answer:
- {short_answer}

Key points:
- This answer was generated from the selected document chunk.
- The response is based only on the retrieved context.

Exam note:
- Review the source file and chunk if you want to check the original note.

Source file: {filename}
Source chunk ID: {chunk_id}
Relevance score: {score}
"""