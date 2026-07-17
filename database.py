import sqlite3
import json

from embeddings import create_simple_embedding


def create_database():
    connection = sqlite3.connect("rag.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            embedding TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_chunks_to_database(chunks):
    connection = sqlite3.connect("rag.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM documents")

    for chunk in chunks:
        embedding = create_simple_embedding(chunk)
        embedding_json = json.dumps(embedding)

        cursor.execute(
            "INSERT INTO documents (content, embedding) VALUES (?, ?)",
            (chunk, embedding_json)
        )

    connection.commit()
    connection.close()


def read_chunks_from_database():
    connection = sqlite3.connect("rag.db")
    cursor = connection.cursor()

    cursor.execute("SELECT id, content, embedding FROM documents")
    rows = cursor.fetchall()

    connection.close()

    chunks = []

    for chunk_id, content, embedding_json in rows:
        embedding = json.loads(embedding_json)
        chunks.append((chunk_id, content, embedding))

    return chunks