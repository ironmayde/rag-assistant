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
    print("\nYou can also type a normal question directly.")
    print("\nExamples:")
    print("what is rag")
    print("ask what is rag")
    print("summarize central limit theorem")
    print("quiz limited company")
    print("flashcard central limit theorem")


def handle_question(question, chunks):
    best_chunk = find_best_chunk_with_saved_embeddings(question, chunks)
    answer = generate_foundry_answer(question, best_chunk)
    print(answer)


def handle_summary(topic, chunks):
    best_chunk = find_best_chunk_with_saved_embeddings(topic, chunks)
    summary = generate_foundry_summary(topic, best_chunk)
    print(summary)


def handle_quiz(topic, chunks):
    best_chunk = find_best_chunk_with_saved_embeddings(topic, chunks)
    quiz = generate_foundry_quiz(topic, best_chunk)
    print(quiz)


def handle_flashcards(topic, chunks):
    best_chunk = find_best_chunk_with_saved_embeddings(topic, chunks)
    flashcards = generate_foundry_flashcards(topic, best_chunk)
    print(flashcards)


def main():
    print("RAG Assistant project started!")
    print("\n--- Foundry Local Study Assistant ---")

    chunks = read_chunks_from_database()

    show_help()

    while True:
        user_input = input("\nEnter command or question: ").strip()

        if not user_input:
            print("Please write a command or question.")
            continue

        lower_input = user_input.lower()

        if lower_input == "exit":
            print("Assistant closed.")
            break

        elif lower_input == "help":
            show_help()

        elif lower_input.startswith("ask "):
            question = user_input[4:].strip()

            if not question:
                print("Please write a question after 'ask'.")
                continue

            handle_question(question, chunks)

        elif lower_input.startswith("summarize "):
            topic = user_input[10:].strip()

            if not topic:
                print("Please write a topic after 'summarize'.")
                continue

            handle_summary(topic, chunks)

        elif lower_input.startswith("quiz "):
            topic = user_input[5:].strip()

            if not topic:
                print("Please write a topic after 'quiz'.")
                continue

            handle_quiz(topic, chunks)

        elif lower_input.startswith("flashcard "):
            topic = user_input[10:].strip()

            if not topic:
                print("Please write a topic after 'flashcard'.")
                continue

            handle_flashcards(topic, chunks)

        else:
            handle_question(user_input, chunks)


if __name__ == "__main__":
    main()