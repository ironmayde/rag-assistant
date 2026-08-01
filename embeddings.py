import math

from foundry_local_sdk import Configuration, FoundryLocalManager
from foundry_local_sdk.exception import FoundryLocalException

from search import clean_text


_manager_initialized = False


def get_foundry_manager():
    global _manager_initialized

    if not _manager_initialized:
        config = Configuration(app_name="rag-assistant-embeddings")

        try:
            FoundryLocalManager.initialize(config)
        except FoundryLocalException as error:
            if "singleton" not in str(error).lower():
                raise error

        _manager_initialized = True

    return FoundryLocalManager.instance


def create_foundry_embeddings(texts):
    if not texts:
        return []

    manager = get_foundry_manager()
    model = manager.catalog.get_model("qwen3-embedding-0.6b")

    if not model.is_cached:
        print("Embedding model is being downloaded...")
        model.download()

    model.load()

    try:
        client = model.get_embedding_client()
        response = client.generate_embeddings(texts)

        embeddings = []

        for item in response.data:
            embeddings.append(item.embedding)

        return embeddings

    finally:
        model.unload()


def create_foundry_embedding(text):
    embeddings = create_foundry_embeddings([text])

    if not embeddings:
        return []

    return embeddings[0]


def calculate_cosine_similarity(embedding1, embedding2):
    if not embedding1 or not embedding2:
        return 0.0

    dot_product = 0.0
    magnitude1 = 0.0
    magnitude2 = 0.0

    for value1, value2 in zip(embedding1, embedding2):
        dot_product += value1 * value2
        magnitude1 += value1 * value1
        magnitude2 += value2 * value2

    magnitude1 = math.sqrt(magnitude1)
    magnitude2 = math.sqrt(magnitude2)

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


# Temporary old embedding functions.
# These will be removed after the real vector search is connected successfully.

def create_simple_embedding(text):
    clean = clean_text(text)
    words = clean.split()

    embedding = {}

    for word in words:
        if word in embedding:
            embedding[word] += 1
        else:
            embedding[word] = 1

    return embedding


def calculate_similarity(embedding1, embedding2):
    score = 0

    for word in embedding1:
        if word in embedding2:
            score += min(embedding1[word], embedding2[word])

    return score