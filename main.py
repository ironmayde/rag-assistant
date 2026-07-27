from database import read_chunks_from_database
from embeddings import create_simple_embedding, calculate_similarity
from foundry_answer import (
    generate_foundry_answer,
    generate_foundry_summary,
    generate_foundry_quiz,
    generate_foundry_flashcards
)
from search import clean_text


def find_best_chunk_with_saved_embeddings(question, chunks):
    question_embedding = create_simple_embedding(question)

    best_chunk = None
    best_score = 0

    for chunk_id, filename, content, chunk_embedding in chunks:
        clean_content = clean_text(content)

        score = calculate_similarity(question_embedding, chunk_embedding)

        if score > 0 and "what is" in question.lower():
            if "means" in clean_content:
                score += 2
            if "retrievalaugmented generation" in clean_content:
                score += 2

        if score > best_score:
            best_score = score
            best_chunk = (chunk_id, filename, content, score)

    return best_chunk


def show_help():
    print("\nType one of these commands:")
    print("ask <your question>")
    print("summarize <topic>")
    print("quiz <topic>")
    print("flashcard <topic>")
    print("help")
    print("exit")
    print("\nExamples:")
    print("ask what is rag")
    print("summarize central limit theorem")
    print("quiz limited company")
    print("flashcard central limit theorem")


def main():
    print("RAG Assistant project started!")
    print("\n--- Foundry Local Study Assistant ---")

    chunks = read_chunks_from_database()

    show_help()

    while True:
        user_input = input("\nEnter command: ").strip()

        if user_input.lower() == "exit":
            print("Assistant closed.")
            break

        elif user_input.lower() == "help":
            show_help()

        elif user_input.lower().startswith("ask "):
            question = user_input[4:].strip()

            if not question:
                print("Please write a question after 'ask'.")
                continue

            best_chunk = find_best_chunk_with_saved_embeddings(question, chunks)
            answer = generate_foundry_answer(question, best_chunk)
            print(answer)

        elif user_input.lower().startswith("summarize "):
            topic = user_input[10:].strip()

            if not topic:
                print("Please write a topic after 'summarize'.")
                continue

            best_chunk = find_best_chunk_with_saved_embeddings(topic, chunks)
            summary = generate_foundry_summary(topic, best_chunk)
            print(summary)

        elif user_input.lower().startswith("quiz "):
            topic = user_input[5:].strip()

            if not topic:
                print("Please write a topic after 'quiz'.")
                continue

            best_chunk = find_best_chunk_with_saved_embeddings(topic, chunks)
            quiz = generate_foundry_quiz(topic, best_chunk)
            print(quiz)

        elif user_input.lower().startswith("flashcard "):
            topic = user_input[10:].strip()

            if not topic:
                print("Please write a topic after 'flashcard'.")
                continue

            best_chunk = find_best_chunk_with_saved_embeddings(topic, chunks)
            flashcards = generate_foundry_flashcards(topic, best_chunk)
            print(flashcards)

        else:
            print("Invalid command. Type 'help' to see examples.")


if __name__ == "__main__":
    main()