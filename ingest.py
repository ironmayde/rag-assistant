import os

from database import create_database, save_chunks_to_database


DOCUMENTS_FOLDER = "documents"
ARTIST_FILE_NAME = "art_artist.txt"
MAX_WORDS_PER_CHUNK = 80


def read_txt_files_from_documents_folder():
    all_chunks = []

    for filename in os.listdir(DOCUMENTS_FOLDER):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(
            DOCUMENTS_FOLDER,
            filename
        )

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            content = file.read()

        if filename.lower() == ARTIST_FILE_NAME:
            chunks = split_artist_entries(content)

        else:
            chunks = split_text_into_chunks(content)

        for chunk in chunks:
            all_chunks.append((filename, chunk))

        print(
            f"Loaded {len(chunks)} chunks from {filename}"
        )

    return all_chunks


def split_artist_entries(text):
    chunks = []
    current_section = "Genel sanat tarihi"

    for line in text.splitlines():
        clean_line = line.strip()

        if not clean_line:
            continue

        if "—" not in clean_line:
            current_section = clean_line
            continue

        parts = clean_line.split("—")

        if len(parts) < 3:
            continue

        artwork = parts[0].strip()
        artist = parts[1].strip()
        date = "—".join(parts[2:]).strip()

        structured_chunk = (
            f"Eser: {artwork}; "
            f"Ressam: {artist}; "
            f"Tarih: {date}; "
            f"Sanat dönemi veya akımı: "
            f"{current_section}."
        )

        chunks.append(structured_chunk)

    return chunks


def split_text_into_chunks(text):
    paragraphs = text.split("\n\n")

    chunks = []

    for paragraph in paragraphs:
        clean_paragraph = paragraph.strip()

        if not clean_paragraph:
            continue

        paragraph_chunks = split_long_text_by_word_count(
            clean_paragraph
        )

        for chunk in paragraph_chunks:
            chunks.append(chunk)

    return chunks


def split_long_text_by_word_count(text):
    words = text.split()

    if len(words) <= MAX_WORDS_PER_CHUNK:
        return [text]

    chunks = []

    for start_index in range(
        0,
        len(words),
        MAX_WORDS_PER_CHUNK
    ):
        chunk_words = words[
            start_index:
            start_index + MAX_WORDS_PER_CHUNK
        ]

        chunk = " ".join(chunk_words)
        chunks.append(chunk)

    return chunks


def main():
    print("Document ingestion started.")

    create_database()

    chunks = read_txt_files_from_documents_folder()

    if not chunks:
        print(
            "No chunks found. "
            "Please add .txt files to the documents folder."
        )
        return

    save_chunks_to_database(chunks)

    print(
        f"\nTotal chunks saved to database: "
        f"{len(chunks)}"
    )

    print(
        "Document ingestion completed successfully."
    )


if __name__ == "__main__":
    main()