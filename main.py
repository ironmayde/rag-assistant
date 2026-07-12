import sqlite3
import string


def read_chunks_from_database():
    connection = sqlite3.connect("rag.db")
    cursor = connection.cursor()

    cursor.execute("SELECT id, content FROM documents")
    chunks = cursor.fetchall()

    connection.close()

    return chunks


def clean_text(text):
    text = text.lower()

    for punctuation in string.punctuation:
        text = text.replace(punctuation, "")

    return text


def find_best_chunk(question, chunks):
    stop_words = [
        "what", "is", "the", "a", "an", "do", "does",
        "can", "how", "why", "we", "it"
    ]

    clean_question = clean_text(question)
    question_words = clean_question.split()

    important_words = []

    for word in question_words:
        if word not in stop_words:
            important_words.append(word)

    best_chunk = None
    best_score = 0

    for chunk_id, content in chunks:
        clean_content = clean_text(content)
        score = 0

        for word in important_words:
            if word in clean_content:
                score += 1

        if score > 0 and "what is" in question.lower():
            if "means" in clean_content:
                score += 2
            if "retrievalaugmented generation" in clean_content:
                score += 2

        if score > best_score:
            best_score = score
            best_chunk = (chunk_id, content, score)

    return best_chunk


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


def main():
    print("RAG Assistant project started!")
    print("\n--- Simple RAG Chat ---")
    print("Type 'exit' to close the assistant.\n")

    chunks = read_chunks_from_database()

    while True:
        question = input("Ask a question: ")

        if question.lower() == "exit":
            print("Assistant closed.")
            break

        best_chunk = find_best_chunk(question, chunks)
        answer = generate_simple_answer(best_chunk)

        print(answer)


if __name__ == "__main__":
    main()