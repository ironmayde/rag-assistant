import re

from foundry_local_sdk import Configuration, FoundryLocalManager
from foundry_local_sdk.exception import FoundryLocalException


_manager_initialized = False
MAX_OUTSIDE_WORD_RATIO = 0.20


def get_foundry_manager():
    global _manager_initialized

    if not _manager_initialized:
        config = Configuration(app_name="rag-assistant")

        try:
            FoundryLocalManager.initialize(config)
        except FoundryLocalException as error:
            if "singleton" not in str(error).lower():
                raise error

        _manager_initialized = True

    return FoundryLocalManager.instance


def combine_chunk_contents(relevant_chunks):
    contents = []

    for chunk_id, filename, content, score in relevant_chunks:
        contents.append(content)

    return "\n\n".join(contents)


def create_sources_text(relevant_chunks):
    source_lines = []

    for chunk_id, filename, content, score in relevant_chunks:
        source_lines.append(
            f"- {filename} | Chunk ID: {chunk_id} | "
            f"Relevance score: {score}"
        )

    return "\n".join(source_lines)


def get_unique_filenames(relevant_chunks):
    filenames = []

    for chunk_id, filename, content, score in relevant_chunks:
        if filename not in filenames:
            filenames.append(filename)

    return filenames


def split_context_into_sentences(context):
    sentences = re.split(r"(?<=[.!?])\s+", context.strip())

    clean_sentences = []

    for sentence in sentences:
        clean_sentence = sentence.strip()

        if clean_sentence:
            clean_sentences.append(clean_sentence)

    return clean_sentences


def create_key_points_from_context(context, max_points=3):
    sentences = split_context_into_sentences(context)

    key_points = []

    for sentence in sentences[:max_points]:
        key_points.append(sentence)

    return key_points


def create_safe_short_answer(context):
    sentences = split_context_into_sentences(context)

    if not sentences:
        return "I could not find this information in the document."

    return sentences[0]


def is_answer_too_risky(answer, context):
    if len(answer) > 350:
        return True

    context_words = set(
        re.findall(r"\b[a-zA-Z]{4,}\b", context.lower())
    )

    answer_words = re.findall(
        r"\b[a-zA-Z]{4,}\b",
        answer.lower()
    )

    if not answer_words:
        return True

    outside_words = []

    for word in answer_words:
        if word not in context_words:
            outside_words.append(word)

    outside_ratio = len(outside_words) / len(answer_words)

    if outside_ratio > MAX_OUTSIDE_WORD_RATIO:
        return True

    return False


def create_exam_note(relevant_chunks):
    filenames = get_unique_filenames(relevant_chunks)
    filenames_text = ", ".join(filenames)

    return (
        f"Remember this topic from {filenames_text}; "
        "it may be useful for definition, explanation, "
        "or short-answer exam questions."
    )


def generate_model_response(task_instruction, content, question):
    manager = get_foundry_manager()
    model = manager.catalog.get_model("qwen2.5-0.5b")

    if not model.is_cached:
        model.download()

    model.load()

    try:
        client = model.get_chat_client()

        response = client.complete_chat([
            {
                "role": "system",
                "content": (
                    "You are a local RAG study assistant. "
                    "Use only facts explicitly stated in the provided context. "
                    "Do not add outside knowledge. "
                    "Do not invent details. "
                    "Do not infer causes, trends, changes, or comparisons "
                    "that are not directly written in the context. "
                    "Stay very close to the wording of the context. "
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

        return response.choices[0].message.content.strip()

    finally:
        model.unload()


def generate_foundry_answer(question, relevant_chunks):
    if not relevant_chunks:
        return "I could not find relevant information in the documents."

    context = combine_chunk_contents(relevant_chunks)

    task_instruction = (
        "Write only one clear and short answer sentence. "
        "The sentence must be directly supported by the context."
    )

    model_answer = generate_model_response(
        task_instruction,
        context,
        question
    )

    if is_answer_too_risky(model_answer, context):
        short_answer = create_safe_short_answer(context)
        grounding_note = (
            "The model answer was simplified to stay closer "
            "to the retrieved context."
        )
    else:
        short_answer = model_answer
        grounding_note = (
            "The model answer passed the context-grounding check."
        )

    key_points = create_key_points_from_context(context)
    exam_note = create_exam_note(relevant_chunks)
    sources_text = create_sources_text(relevant_chunks)

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


def generate_foundry_summary(topic, relevant_chunks):
    if not relevant_chunks:
        return "I could not find relevant information in the documents."

    context = combine_chunk_contents(relevant_chunks)
    key_points = create_key_points_from_context(context)
    sources_text = create_sources_text(relevant_chunks)

    summary_text = ""

    for point in key_points:
        summary_text += f"- {point}\n"

    return f"""
Summary:
{summary_text}
Sources:
{sources_text}
"""


def generate_foundry_quiz(topic, relevant_chunks):
    if not relevant_chunks:
        return "I could not find relevant information in the documents."

    context = combine_chunk_contents(relevant_chunks)
    key_points = create_key_points_from_context(context)
    sources_text = create_sources_text(relevant_chunks)

    quiz_text = ""

    for index, point in enumerate(key_points, start=1):
        quiz_text += (
            f"Question {index}: "
            "What should you remember about this topic?\n"
        )
        quiz_text += f"Answer {index}: {point}\n\n"

    return f"""
Quiz:
{quiz_text}
Sources:
{sources_text}
"""


def generate_foundry_flashcards(topic, relevant_chunks):
    if not relevant_chunks:
        return "I could not find relevant information in the documents."

    context = combine_chunk_contents(relevant_chunks)
    key_points = create_key_points_from_context(context)
    sources_text = create_sources_text(relevant_chunks)

    flashcards_text = ""

    for index, point in enumerate(key_points, start=1):
        flashcards_text += f"Card {index}\n"
        flashcards_text += "Q: What should you remember?\n"
        flashcards_text += f"A: {point}\n\n"

    return f"""
Flashcards:
{flashcards_text}
Sources:
{sources_text}
"""