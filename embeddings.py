from search import clean_text


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