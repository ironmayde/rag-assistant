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


def create_exam_note(filename):
    return (
        f"Remember this topic from {filename}; it may be useful for definition, "
        f"explanation, or short-answer exam questions."
    )


def generate_model_response(task_instruction, content, question):
    manager = get_foundry_manager()
    model = manager.catalog.get_model("qwen2.5-0.5b")

    if not model.is_cached:
        model.download()

    model.load()
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

    answer = response.choices[0].message.content.strip()

    model.unload()

    return answer


def generate_foundry_answer(question, best_chunk):
    if best_chunk is None:
        return "I could not find relevant information in the documents."

    chunk_id, filename, content, score = best_chunk

    task_instruction = (
        "Write only one clear and short answer sentence. "
        "The sentence must be directly supported by the context."
    )

    model_answer = generate_model_response(
        task_instruction,
        content,
        question
    )

    if is_answer_too_risky(model_answer, content):
        short_answer = create_safe_short_answer(content)
        grounding_note = (
            "The model answer was simplified to stay closer "
            "to the retrieved context."
        )
    else:
        short_answer = model_answer
        grounding_note = (
            "The model answer passed the context-grounding check."
        )

    key_points = create_key_points_from_context(content)
    exam_note = create_exam_note(filename)

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

Source file: {filename}
Source chunk ID: {chunk_id}
Relevance score: {score}
"""


def generate_foundry_summary(topic, best_chunk):
    if best_chunk is None:
        return "I could not find relevant information in the documents."

    chunk_id, filename, content, score = best_chunk

    key_points = create_key_points_from_context(content)

    summary_text = ""

    for point in key_points:
        summary_text += f"- {point}\n"

    return f"""
Summary:
{summary_text}
Source file: {filename}
Source chunk ID: {chunk_id}
Relevance score: {score}
"""


def generate_foundry_quiz(topic, best_chunk):
    if best_chunk is None:
        return "I could not find relevant information in the documents."

    chunk_id, filename, content, score = best_chunk

    key_points = create_key_points_from_context(content)

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
Source file: {filename}
Source chunk ID: {chunk_id}
Relevance score: {score}
"""


def generate_foundry_flashcards(topic, best_chunk):
    if best_chunk is None:
        return "I could not find relevant information in the documents."

    chunk_id, filename, content, score = best_chunk

    key_points = create_key_points_from_context(content)

    flashcards_text = ""

    for index, point in enumerate(key_points, start=1):
        flashcards_text += f"Card {index}\n"
        flashcards_text += "Q: What should you remember?\n"
        flashcards_text += f"A: {point}\n\n"

    return f"""
Flashcards:
{flashcards_text}
Source file: {filename}
Source chunk ID: {chunk_id}
Relevance score: {score}
"""