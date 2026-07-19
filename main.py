from database import read_chunks_from_database
from embeddings import create_simple_embedding, calculate_similarity
from foundry_answer import generate_foundry_answer
from search import clean_text


def find_best_chunk_with_saved_embeddings(question, chunks):
    question_embedding = create_simple_embedding(question)

    best_chunk = None
    best_score = 0

    for chunk_id, content, chunk_embedding in chunks:
        clean_content = clean_text(content)

        score = calculate_similarity(question_embedding, chunk_embedding)

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
    print("\n--- Foundry Local RAG Chat ---")
    print("Type 'exit' to close the assistant.\n")

    chunks = read_chunks_from_database()

    while True:
        question = input("Ask a question: ")

        if question.lower() == "exit":
            print("Assistant closed.")
            break

        best_chunk = find_best_chunk_with_saved_embeddings(question, chunks)
        answer = generate_foundry_answer(question, best_chunk)

        print(answer)


if __name__ == "__main__":
    main()