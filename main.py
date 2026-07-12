from database import read_chunks_from_database
from search import find_best_chunk
from answer import generate_simple_answer


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