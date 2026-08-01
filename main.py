import re
import unicodedata

from database import read_chunks_from_database
from embeddings import (
    create_foundry_embedding,
    calculate_cosine_similarity
)
from foundry_answer import (
    generate_foundry_answer,
    generate_foundry_summary,
    generate_foundry_quiz,
    generate_foundry_flashcards
)


ARTIST_FILE_NAME = "art_artist.txt"
MIN_RELEVANCE_SCORE = 0.35
MAX_SCORE_GAP = 0.10
TOP_K = 2


def normalize_for_exact_match(text):
    normalized_text = text.casefold()

    normalized_text = unicodedata.normalize(
        "NFKD",
        normalized_text
    )

    normalized_text = "".join(
        character
        for character in normalized_text
        if not unicodedata.combining(character)
    )

    normalized_text = normalized_text.replace(
        "ı",
        "i"
    )

    normalized_text = re.sub(
        r"[^\w\s]",
        " ",
        normalized_text,
        flags=re.UNICODE
    )

    return " ".join(normalized_text.split())


def extract_artwork_title(content):
    if not content.startswith("Eser:"):
        return None

    first_field = content.split(";", 1)[0]

    if ":" not in first_field:
        return None

    field_name, field_value = first_field.split(
        ":",
        1
    )

    if field_name.strip().lower() != "eser":
        return None

    return field_value.strip()


def find_exact_artwork_chunks(
    question,
    chunks
):
    normalized_question = (
        normalize_for_exact_match(question)
    )

    padded_question = (
        f" {normalized_question} "
    )

    exact_matches = []

    for (
        chunk_id,
        filename,
        content,
        chunk_embedding
    ) in chunks:
        if filename.lower() != ARTIST_FILE_NAME:
            continue

        artwork_title = extract_artwork_title(
            content
        )

        if not artwork_title:
            continue

        normalized_title = (
            normalize_for_exact_match(
                artwork_title
            )
        )

        padded_title = f" {normalized_title} "

        if padded_title in padded_question:
            exact_matches.append(
                (
                    len(normalized_title),
                    (
                        chunk_id,
                        filename,
                        content,
                        1.0
                    )
                )
            )

    if not exact_matches:
        return []

    longest_title_length = max(
        title_length
        for title_length, chunk
        in exact_matches
    )

    longest_matches = []

    for title_length, chunk in exact_matches:
        if title_length == longest_title_length:
            longest_matches.append(chunk)

    return longest_matches[:TOP_K]


def find_top_chunks_with_saved_embeddings(
    question,
    chunks
):
    exact_artwork_chunks = (
        find_exact_artwork_chunks(
            question,
            chunks
        )
    )

    if exact_artwork_chunks:
        return exact_artwork_chunks

    question_embedding = create_foundry_embedding(
        question
    )

    candidate_chunks = []

    for (
        chunk_id,
        filename,
        content,
        chunk_embedding
    ) in chunks:
        if len(question_embedding) != len(
            chunk_embedding
        ):
            continue

        score = calculate_cosine_similarity(
            question_embedding,
            chunk_embedding
        )

        if score >= MIN_RELEVANCE_SCORE:
            candidate_chunks.append(
                (
                    chunk_id,
                    filename,
                    content,
                    round(score, 4)
                )
            )

    candidate_chunks.sort(
        key=lambda chunk: chunk[3],
        reverse=True
    )

    if not candidate_chunks:
        return []

    best_score = candidate_chunks[0][3]
    relevant_chunks = []

    for chunk in candidate_chunks:
        score = chunk[3]
        score_gap = best_score - score

        if score_gap <= MAX_SCORE_GAP:
            relevant_chunks.append(chunk)

        if len(relevant_chunks) == TOP_K:
            break

    return relevant_chunks


def show_help():
    print("\nType one of these commands:")
    print("ask <your question>")
    print("summarize <topic>")
    print("quiz <topic>")
    print("flashcard <topic>")
    print("help")
    print("exit")

    print(
        "\nYou can also type a normal "
        "question directly."
    )

    print("\nExamples:")
    print("what is rag")
    print("ask what is rag")
    print("summarize central limit theorem")
    print("quiz limited company")
    print("flashcard central limit theorem")


def handle_question(question, chunks):
    relevant_chunks = (
        find_top_chunks_with_saved_embeddings(
            question,
            chunks
        )
    )

    answer = generate_foundry_answer(
        question,
        relevant_chunks
    )

    print(answer)


def handle_summary(topic, chunks):
    relevant_chunks = (
        find_top_chunks_with_saved_embeddings(
            topic,
            chunks
        )
    )

    summary = generate_foundry_summary(
        topic,
        relevant_chunks
    )

    print(summary)


def handle_quiz(topic, chunks):
    relevant_chunks = (
        find_top_chunks_with_saved_embeddings(
            topic,
            chunks
        )
    )

    quiz = generate_foundry_quiz(
        topic,
        relevant_chunks
    )

    print(quiz)


def handle_flashcards(topic, chunks):
    relevant_chunks = (
        find_top_chunks_with_saved_embeddings(
            topic,
            chunks
        )
    )

    flashcards = generate_foundry_flashcards(
        topic,
        relevant_chunks
    )

    print(flashcards)


def main():
    print("RAG Assistant project started!")

    print(
        "\n--- Foundry Local Study Assistant ---"
    )

    chunks = read_chunks_from_database()

    show_help()

    while True:
        user_input = input(
            "\nEnter command or question: "
        ).strip()

        if not user_input:
            print(
                "Please write a command or question."
            )
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
                print(
                    "Please write a question "
                    "after 'ask'."
                )
                continue

            handle_question(question, chunks)

        elif lower_input.startswith("summarize "):
            topic = user_input[10:].strip()

            if not topic:
                print(
                    "Please write a topic "
                    "after 'summarize'."
                )
                continue

            handle_summary(topic, chunks)

        elif lower_input.startswith("quiz "):
            topic = user_input[5:].strip()

            if not topic:
                print(
                    "Please write a topic "
                    "after 'quiz'."
                )
                continue

            handle_quiz(topic, chunks)

        elif lower_input.startswith("flashcard "):
            topic = user_input[10:].strip()

            if not topic:
                print(
                    "Please write a topic "
                    "after 'flashcard'."
                )
                continue

            handle_flashcards(topic, chunks)

        else:
            handle_question(
                user_input,
                chunks
            )


if __name__ == "__main__":
    main()