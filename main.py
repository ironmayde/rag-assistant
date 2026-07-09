import sqlite3


def read_chunks_from_database():
    connection = sqlite3.connect("rag.db")
    cursor = connection.cursor()

    cursor.execute("SELECT id, content FROM documents")
    rows = cursor.fetchall()

    connection.close()

    return rows


def main():
    print("RAG Assistant project started!")
    print("\n--- Chunks from Database ---")

    chunks = read_chunks_from_database()

    for chunk_id, content in chunks:
        print(f"\nID: {chunk_id}")
        print(f"Content: {content}")


if __name__ == "__main__":
    main()