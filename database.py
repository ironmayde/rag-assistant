import json
import sqlite3

from embeddings import create_foundry_embeddings


def create_database():
    connection = sqlite3.connect("rag.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_chunks_to_database(chunks):
    texts = []

    for filename, chunk in chunks:
        texts.append(chunk)

    print("\nGenerating Foundry Local embeddings...")
    embeddings = create_foundry_embeddings(texts)

    if len(embeddings) != len(chunks):
        raise ValueError(
            "The number of generated embeddings does not match the number of chunks."
        )

    connection = sqlite3.connect("rag.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM documents")

    for (filename, chunk), embedding in zip(chunks, embeddings):
        embedding_json = json.dumps(embedding)

        cursor.execute(
            """
            INSERT INTO documents (filename, content, embedding)
            VALUES (?, ?, ?)
            """,
            (filename, chunk, embedding_json)
        )

    connection.commit()
    connection.close()


def read_chunks_from_database():
    connection = sqlite3.connect("rag.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, filename, content, embedding FROM documents"
    )

    rows = cursor.fetchall()
    connection.close()

    chunks = []

    for chunk_id, filename, content, embedding_json in rows:
        embedding = json.loads(embedding_json)
        chunks.append((chunk_id, filename, content, embedding))

    return chunks