import os

from database import create_database, save_chunks_to_database


DOCUMENTS_FOLDER = "documents"


def read_txt_files_from_documents_folder():
    all_chunks = []

    for filename in os.listdir(DOCUMENTS_FOLDER):
        if filename.endswith(".txt"):
            file_path = os.path.join(DOCUMENTS_FOLDER, filename)

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            chunks = split_text_into_chunks(content)

            for chunk in chunks:
                all_chunks.append(chunk)

            print(f"Loaded {len(chunks)} chunks from {filename}")

    return all_chunks


def split_text_into_chunks(text):
    paragraphs = text.split("\n\n")

    chunks = []

    for paragraph in paragraphs:
        clean_paragraph = paragraph.strip()

        if clean_paragraph:
            chunks.append(clean_paragraph)

    return chunks


def main():
    print("Document ingestion started.")

    create_database()

    chunks = read_txt_files_from_documents_folder()

    if not chunks:
        print("No chunks found. Please add .txt files to the documents folder.")
        return

    save_chunks_to_database(chunks)

    print(f"\nTotal chunks saved to database: {len(chunks)}")
    print("Document ingestion completed successfully.")


if __name__ == "__main__":
    main()