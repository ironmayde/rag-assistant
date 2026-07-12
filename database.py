import sqlite3


def read_chunks_from_database():
    connection = sqlite3.connect("rag.db")
    cursor = connection.cursor()

    cursor.execute("SELECT id, content FROM documents")
    chunks = cursor.fetchall()

    connection.close()

    return chunks