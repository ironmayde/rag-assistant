import re

from foundry_local_sdk import (
    Configuration,
    FoundryLocalManager
)
from foundry_local_sdk.exception import (
    FoundryLocalException
)


_manager_initialized = False
MAX_OUTSIDE_WORD_RATIO = 0.20
ARTIST_FILE_NAME = "art_artist.txt"


def get_foundry_manager():
    global _manager_initialized

    if not _manager_initialized:
        config = Configuration(
            app_name="rag-assistant"
        )

        try:
            FoundryLocalManager.initialize(config)

        except FoundryLocalException as error:
            if "singleton" not in str(error).lower():
                raise error

        _manager_initialized = True

    return FoundryLocalManager.instance


def combine_chunk_contents(relevant_chunks):
    contents = []

    for (
        chunk_id,
        filename,
        content,
        score
    ) in relevant_chunks:
        contents.append(content)

    return "\n\n".join(contents)


def create_sources_text(relevant_chunks):
    source_lines = []

    for (
        chunk_id,
        filename,
        content,
        score
    ) in relevant_chunks:
        source_lines.append(
            f"- {filename} | "
            f"Chunk ID: {chunk_id} | "
            f"Relevance score: {score}"
        )

    return "\n".join(source_lines)


def get_unique_filenames(relevant_chunks):
    filenames = []

    for (
        chunk_id,
        filename,
        content,
        score
    ) in relevant_chunks:
        if filename not in filenames:
            filenames.append(filename)

    return filenames


def split_context_into_sentences(context):
    sentences = re.split(
        r"(?<=[.!?])\s+",
        context.strip()
    )

    clean_sentences = []

    for sentence in sentences:
        clean_sentence = sentence.strip()

        if clean_sentence:
            clean_sentences.append(
                clean_sentence
            )

    return clean_sentences


def create_key_points_from_context(
    context,
    max_points=3
):
    paragraphs = context.split("\n\n")
    key_points = []

    for paragraph in paragraphs:
        clean_paragraph = paragraph.strip()

        if not clean_paragraph:
            continue

        if clean_paragraph.startswith("Eser:"):
            key_points.append(clean_paragraph)

        else:
            sentences = split_context_into_sentences(
                clean_paragraph
            )

            for sentence in sentences:
                key_points.append(sentence)

                if len(key_points) == max_points:
                    return key_points

        if len(key_points) == max_points:
            return key_points

    return key_points


def create_safe_short_answer(context):
    paragraphs = context.split("\n\n")

    for paragraph in paragraphs:
        clean_paragraph = paragraph.strip()

        if clean_paragraph:
            return clean_paragraph

    return (
        "I could not find this information "
        "in the document."
    )


def get_words(text):
    return re.findall(
        r"\b[^\W\d_]{4,}\b",
        text.lower(),
        flags=re.UNICODE
    )


def is_answer_too_risky(answer, context):
    if len(answer) > 350:
        return True

    context_words = set(get_words(context))
    answer_words = get_words(answer)

    if not answer_words:
        return True

    outside_words = []

    for word in answer_words:
        if word not in context_words:
            outside_words.append(word)

    outside_ratio = (
        len(outside_words) / len(answer_words)
    )

    if outside_ratio > MAX_OUTSIDE_WORD_RATIO:
        return True

    return False


def create_exam_note(relevant_chunks):
    filenames = get_unique_filenames(
        relevant_chunks
    )

    filenames_text = ", ".join(filenames)

    return (
        f"Remember this topic from "
        f"{filenames_text}; "
        "it may be useful for definition, "
        "explanation, or short-answer "
        "exam questions."
    )


def parse_artist_chunk(content):
    fields = {}

    clean_content = content.strip().rstrip(".")

    for section in clean_content.split(";"):
        clean_section = section.strip()

        if ":" not in clean_section:
            continue

        field_name, field_value = (
            clean_section.split(":", 1)
        )

        fields[
            field_name.strip().lower()
        ] = field_value.strip()

    artwork = fields.get("eser")
    artist = fields.get("ressam")
    date = fields.get("tarih")
    movement = fields.get(
        "sanat dönemi veya akımı"
    )

    if not artwork or not artist:
        return None

    return {
        "artwork": artwork,
        "artist": artist,
        "date": date,
        "movement": movement
    }


def question_is_english(question):
    english_markers = [
        "who",
        "what",
        "when",
        "which",
        "painted",
        "created",
        "artist",
        "year"
    ]

    question_words = question.lower().split()

    for marker in english_markers:
        if marker in question_words:
            return True

    return False


def create_artist_answer(question, art_data):
    artwork = art_data["artwork"]
    artist = art_data["artist"]
    date = art_data.get("date")
    movement = art_data.get("movement")

    lower_question = question.lower()

    artist_markers = [
        "kim",
        "kimin",
        "ressam",
        "who",
        "painted",
        "artist"
    ]

    date_markers = [
        "ne zaman",
        "hangi yıl",
        "tarih",
        "when",
        "what year"
    ]

    movement_markers = [
        "hangi akım",
        "hangi dönem",
        "akımı",
        "dönemi",
        "movement",
        "period"
    ]

    asks_for_artist = any(
        marker in lower_question
        for marker in artist_markers
    )

    asks_for_date = any(
        marker in lower_question
        for marker in date_markers
    )

    asks_for_movement = any(
        marker in lower_question
        for marker in movement_markers
    )

    is_english = question_is_english(question)

    if asks_for_artist:
        if is_english:
            return (
                f"{artwork} was created by "
                f"{artist}."
            )

        return (
            f"{artwork}, {artist} "
            "tarafından yapılmıştır."
        )

    if asks_for_date and date:
        if is_english:
            return (
                f"{artwork} dates to {date}."
            )

        return (
            f"{artwork} adlı eserin tarihi: "
            f"{date}."
        )

    if asks_for_movement and movement:
        if is_english:
            return (
                f"{artwork} is listed under "
                f"{movement}."
            )

        return (
            f"{artwork}, {movement} "
            "kategorisinde yer almaktadır."
        )

    if is_english:
        return (
            f"{artwork} was created by "
            f"{artist}. "
            f"Date: {date}. "
            f"Category: {movement}."
        )

    return (
        f"{artwork}, {artist} tarafından "
        f"yapılmıştır. "
        f"Tarih: {date}. "
        f"Kategori: {movement}."
    )


def generate_model_response(
    task_instruction,
    content,
    question
):
    manager = get_foundry_manager()

    model = manager.catalog.get_model(
        "qwen2.5-0.5b"
    )

    if not model.is_cached:
        model.download()

    model.load()

    try:
        client = model.get_chat_client()

        response = client.complete_chat([
            {
                "role": "system",
                "content": (
                    "You are a local RAG study "
                    "assistant. "
                    "Use only facts explicitly "
                    "stated in the provided context. "
                    "Do not add outside knowledge. "
                    "Do not invent details. "
                    "Do not infer causes, trends, "
                    "changes, or comparisons that "
                    "are not directly written in "
                    "the context. "
                    "Answer in the same language as "
                    "the user request. "
                    "Stay very close to the wording "
                    "of the context. "
                    f"{task_instruction}"
                )
            },
            {
                "role": "user",
                "content": f"""
Context:
{content}

User request:
{question}
"""
            }
        ])

        return (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

    finally:
        model.unload()


def generate_foundry_answer(
    question,
    relevant_chunks
):
    if not relevant_chunks:
        return (
            "I could not find relevant "
            "information in the documents."
        )

    context = combine_chunk_contents(
        relevant_chunks
    )

    primary_chunk = relevant_chunks[0]
    primary_filename = primary_chunk[1]
    primary_content = primary_chunk[2]

    if (
        primary_filename.lower()
        == ARTIST_FILE_NAME
    ):
        art_data = parse_artist_chunk(
            primary_content
        )

    else:
        art_data = None

    if art_data:
        short_answer = create_artist_answer(
            question,
            art_data
        )

        grounding_note = (
            "The answer was generated directly "
            "from the structured art record."
        )

    else:
        task_instruction = (
            "Write only one clear and short "
            "answer sentence. "
            "The sentence must be directly "
            "supported by the context."
        )

        model_answer = generate_model_response(
            task_instruction,
            context,
            question
        )

        if is_answer_too_risky(
            model_answer,
            context
        ):
            short_answer = (
                create_safe_short_answer(context)
            )

            grounding_note = (
                "The model answer was simplified "
                "to stay closer to the retrieved "
                "context."
            )

        else:
            short_answer = model_answer

            grounding_note = (
                "The model answer passed the "
                "context-grounding check."
            )

    key_points = create_key_points_from_context(
        context
    )

    exam_note = create_exam_note(
        relevant_chunks
    )

    sources_text = create_sources_text(
        relevant_chunks
    )

    key_points_text = ""

    for point in key_points:
        key_points_text += f"- {point}\n"

    return f"""
Answer:
Short answer:
- {short_answer}

Key points:
{key_points_text}
Exam note:
- {exam_note}

Grounding note:
- {grounding_note}

Sources:
{sources_text}
"""


def generate_foundry_summary(
    topic,
    relevant_chunks
):
    if not relevant_chunks:
        return (
            "I could not find relevant "
            "information in the documents."
        )

    context = combine_chunk_contents(
        relevant_chunks
    )

    key_points = create_key_points_from_context(
        context
    )

    sources_text = create_sources_text(
        relevant_chunks
    )

    summary_text = ""

    for point in key_points:
        summary_text += f"- {point}\n"

    return f"""
Summary:
{summary_text}
Sources:
{sources_text}
"""


def generate_foundry_quiz(
    topic,
    relevant_chunks
):
    if not relevant_chunks:
        return (
            "I could not find relevant "
            "information in the documents."
        )

    context = combine_chunk_contents(
        relevant_chunks
    )

    key_points = create_key_points_from_context(
        context
    )

    sources_text = create_sources_text(
        relevant_chunks
    )

    quiz_text = ""

    for index, point in enumerate(
        key_points,
        start=1
    ):
        quiz_text += (
            f"Question {index}: "
            "What should you remember "
            "about this topic?\n"
        )

        quiz_text += (
            f"Answer {index}: {point}\n\n"
        )

    return f"""
Quiz:
{quiz_text}
Sources:
{sources_text}
"""


def generate_foundry_flashcards(
    topic,
    relevant_chunks
):
    if not relevant_chunks:
        return (
            "I could not find relevant "
            "information in the documents."
        )

    context = combine_chunk_contents(
        relevant_chunks
    )

    key_points = create_key_points_from_context(
        context
    )

    sources_text = create_sources_text(
        relevant_chunks
    )

    flashcards_text = ""

    for index, point in enumerate(
        key_points,
        start=1
    ):
        flashcards_text += (
            f"Card {index}\n"
        )

        flashcards_text += (
            "Q: What should you remember?\n"
        )

        flashcards_text += (
            f"A: {point}\n\n"
        )

    return f"""
Flashcards:
{flashcards_text}
Sources:
{sources_text}
"""