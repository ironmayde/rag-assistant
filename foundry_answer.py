from foundry_local_sdk import Configuration, FoundryLocalManager


def generate_foundry_answer(question, best_chunk):
    if best_chunk is None:
        return "I could not find relevant information in the documents."

    chunk_id, content, score = best_chunk

    config = Configuration(app_name="rag-assistant")
    FoundryLocalManager.initialize(config)

    manager = FoundryLocalManager.instance
    model = manager.catalog.get_model("qwen2.5-0.5b")

    if not model.is_cached:
        model.download()

    model.load()
    client = model.get_chat_client()

    response = client.complete_chat([
        {
            "role": "system",
            "content": (
                "You are a local RAG assistant. "
                "Answer the user's question only using the provided context. "
                "If the answer is not in the context, say that you cannot find it in the document. "
                "Answer briefly and clearly."
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

    answer = response.choices[0].message.content

    model.unload()

    return f"""
Answer:
{answer}

Source chunk ID: {chunk_id}
Relevance score: {score}
"""