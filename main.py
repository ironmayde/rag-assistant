from database import read_chunks_from_database
from embeddings import create_simple_embedding, calculate_similarity


def main():
    print("RAG Assistant project started!")
    print("\n--- Simple Embedding Similarity Search ---")

    question = input("Ask a question: ")

    question_embedding = create_simple_embedding(question)
    chunks = read_chunks_from_database()

    best_chunk = None
    best_score = 0

    for chunk_id, content in chunks:
        chunk_embedding = create_simple_embedding(content)
        score = calculate_similarity(question_embedding, chunk_embedding)

        if score > best_score:
            best_score = score
            best_chunk = (chunk_id, content, score)

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