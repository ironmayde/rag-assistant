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

        # Tanım sorularında sadece ilgili chunk'a ekstra puan ver
        if score > 0 and "what is" in question.lower():
            if "means" in clean_content:
                score += 2
            if "retrievalaugmented generation" in clean_content:
                score += 2

        if score > best_score:
            best_score = score
            best_chunk = (chunk_id, content, score)

    return best_chunk


def main():
    print("RAG Assistant project started!")
    print("\n--- Question-Based Search ---")

    question = input("Ask a question: ")

    chunks = read_chunks_from_database()
    best_chunk = find_best_chunk(question, chunks)

    if best_chunk:
        chunk_id, content, score = best_chunk

        print("\nBest matching chunk:")
        print(f"ID: {chunk_id}")
        print(f"Score: {score}")
        print(f"Content: {content}")
    else:
        print("\nNo relevant chunk found.")


if __name__ == "__main__":
    main()