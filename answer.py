def generate_simple_answer(best_chunk):
    if best_chunk is None:
        return "I could not find relevant information in the documents."

    chunk_id, content, score = best_chunk

    answer = f"""
Answer:
Based on the document, {content}

Source chunk ID: {chunk_id}
Relevance score: {score}
"""

    return answer