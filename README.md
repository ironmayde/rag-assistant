# Local RAG Study Assistant with Microsoft Foundry Local

A local Retrieval-Augmented Generation (RAG) study assistant built with Python, SQLite, Streamlit, and Microsoft Foundry Local.

The application searches local study documents using semantic vector search and exact artwork matching. It then generates source-grounded answers and study materials with an on-device language model.

After the required models are downloaded, the application can run without an internet connection.

## Project Goal

The goal of this project is to create an offline-capable assistant that helps students study from their own documents.

The project demonstrates the three main stages of RAG:

1. Retrieve relevant information from local documents.
2. Augment the model input with retrieved context.
3. Generate an answer grounded in that context.

## Main Features

- Reads local `.txt` documents
- Splits documents into manageable chunks
- Supports a structured artist–artwork dataset
- Generates real Foundry Local embeddings
- Stores 1024-dimensional vectors in SQLite
- Processes large document collections in batches
- Uses cosine similarity for semantic search
- Uses exact artwork-title matching
- Combines exact and semantic search through hybrid retrieval
- Retrieves up to two relevant chunks
- Removes weak secondary results with dynamic top-k filtering
- Rejects unrelated questions with a relevance threshold
- Generates answers using a local chat model
- Applies grounding checks to reduce unsupported output
- Produces deterministic answers from structured art records
- Supports Turkish and English questions
- Includes CLI and Streamlit interfaces
- Supports Ask, Summarize, Quiz, and Flashcards modes
- Displays source files, chunk IDs, and relevance scores
- Runs locally after model installation

## Technologies

- Python 3.12
- SQLite
- Streamlit
- Microsoft Foundry Local
- Foundry Local SDK
- Qwen3 Embedding 0.6B
- Qwen2.5 0.5B
- Cosine similarity
- Hybrid retrieval
- JSON
- Git and GitHub

## Models

### Embedding model

```text
qwen3-embedding-0.6b
```

This model converts documents and user questions into 1024-dimensional numerical vectors.

### Chat model

```text
qwen2.5-0.5b
```

This lightweight model generates answers from retrieved context on the user’s device.

## Project Structure

```text
rag-assistant/
│
├── documents/
│   ├── art_artist.txt
│   ├── commercial_law_notes.txt
│   ├── project_notes.txt
│   └── statistics_notes.txt
│
├── app.py
├── database.py
├── embedding_test.py
├── embeddings.py
├── foundry_answer.py
├── foundry_test.py
├── ingest.py
├── main.py
├── rag.db
├── requirements.txt
└── README.md
```

## Knowledge Base

The current knowledge base contains four documents:

| File | Content |
|---|---|
| `project_notes.txt` | RAG and project information |
| `statistics_notes.txt` | Statistics study notes |
| `commercial_law_notes.txt` | Commercial law study notes |
| `art_artist.txt` | Artist, artwork, date, and art-period records |

The current database contains:

```text
194 chunks
```

Of these, 179 chunks come from `art_artist.txt`.

## Document Ingestion

`ingest.py` reads every `.txt` file in the `documents` folder.

Normal study documents are split by paragraph and word count.

The `art_artist.txt` file uses a special parser. Every artwork line is converted into a structured chunk:

```text
Eser: Öpücük; Ressam: Gustav Klimt; Tarih: 1907–1908; Sanat dönemi veya akımı: Ekspresyonizm ve sembolizm.
```

This structure makes artwork, artist, date, and art-period information easier to retrieve reliably.

## Batch Embedding Generation

Sending all 194 chunks to the embedding model in one request caused the operation to be cancelled.

The ingestion system was therefore updated to process embeddings in batches:

```text
EMBEDDING_BATCH_SIZE = 10
```

Example output:

```text
Generating embedding batch 1/20...
Generating embedding batch 2/20...
...
Generating embedding batch 20/20...
```

This allows larger document collections to be processed reliably on local hardware.

## Running the Ingestion Pipeline

Run:

```bat
python ingest.py
```

Example output:

```text
Document ingestion started.
Loaded 179 chunks from art_artist.txt
Loaded 5 chunks from commercial_law_notes.txt
Loaded 5 chunks from project_notes.txt
Loaded 5 chunks from statistics_notes.txt

Generating Foundry Local embeddings...
Generating embedding batch 1/20...
...
Generating embedding batch 20/20...

Total chunks saved to database: 194
Document ingestion completed successfully.
```

Run `ingest.py` again whenever a document is added, removed, or changed.

## Retrieval Pipeline

### 1. Exact artwork matching

When a question contains an artwork title, the system first searches for an exact normalized title match.

Punctuation, capitalization, accents, and apostrophes are normalized.

Example:

```text
Öpücük'ün ressamı kimdir?
```

The system directly matches:

```text
Eser: Öpücük
```

Exact artwork matches use:

```text
Relevance score: 1.0
```

This value represents a confirmed title match rather than cosine similarity.

### 2. Longest-title selection

Some artwork titles contain other artwork titles.

For example:

```text
Son Akşam Yemeği
Son Akşam Yemeği Ayini
```

When both could match, the system selects the longest matching title.

### 3. Semantic vector search

If no exact artwork title is found, the query is converted into an embedding.

The query vector is compared with every stored document vector using cosine similarity.

### 4. Minimum relevance threshold

The current minimum semantic relevance score is:

```text
0.35
```

If no result reaches this value, the system returns:

```text
I could not find relevant information in the documents.
```

### 5. Dynamic top-k retrieval

The application can retrieve up to two chunks:

```text
TOP_K = 2
```

However, the second result is only accepted if its score is close to the best result:

```text
MAX_SCORE_GAP = 0.10
```

This prevents unrelated secondary chunks from contaminating an otherwise correct answer.

## Answer Generation

For regular study documents, retrieved context is sent to the local Qwen chat model.

The model is instructed to:

- Use only explicitly stated context
- Avoid outside knowledge
- Avoid invented information
- Answer in the same language as the user
- Avoid unsupported causes, comparisons, or trends

A grounding check examines the generated response. Risky responses are replaced with safer context-based text.

## Structured Art Answers

For records from `art_artist.txt`, the application generates answers directly from the structured fields.

Example question:

```text
Kaplumbağa Terbiyecisi kimin eseridir?
```

Example answer:

```text
Kaplumbağa Terbiyecisi, Osman Hamdi Bey tarafından yapılmıştır.
```

Example date question:

```text
Guernica ne zaman yapıldı?
```

Example answer:

```text
Guernica adlı eserin tarihi: 1937.
```

This prevents the small language model from combining unrelated artist records.

## Running the Streamlit Interface

Start the web interface:

```bat
streamlit run app.py
```

The application normally opens at:

```text
http://localhost:8501
```

The interface displays:

- Number of documents
- Number of stored chunks
- Top-k setting
- Available document names
- Local model information
- Study-mode selection
- Formatted results
- Retrieved sources and scores

Stop the application with:

```text
Ctrl + C
```

## Running the CLI Interface

The original command-line interface remains available:

```bat
python main.py
```

## Study Modes

### Ask

```text
What is RAG?
```

```text
Öpücük'ün ressamı kimdir?
```

### Summarize

```text
summarize central limit theorem
```

### Quiz

```text
quiz limited company
```

### Flashcards

```text
flashcard central limit theorem
```

## Successful Test Examples

### Semantic retrieval

Question:

```text
What happens to the distribution of averages when the sample size grows?
```

Retrieved source:

```text
statistics_notes.txt
```

The question does not contain the phrase “Central Limit Theorem,” but the correct topic was found through semantic similarity.

### Unknown information

Question:

```text
Who painted the Mona Lisa?
```

Before the art document was added, the assistant correctly reported that the information was unavailable.

After `art_artist.txt` was added and the database was regenerated, the assistant answered:

```text
The Mona Lisa was created by Leonardo da Vinci.
```

This demonstrates that the assistant’s knowledge can be expanded by adding local documents.

### Hybrid retrieval correction

The question:

```text
Öpücük'ün ressamı kimdir?
```

initially produced an unrelated semantic result.

After exact artwork matching was added, the correct result became:

```text
Öpücük, Gustav Klimt tarafından yapılmıştır.
```

## Testing Scripts

Test the chat model:

```bat
python foundry_test.py
```

Test the embedding model:

```bat
python embedding_test.py
```

The embedding test confirms that the model produces a 1024-dimensional vector.

## Offline Operation

The Streamlit interface, SQLite database, embedding model, and chat model all run locally.

After the models have been downloaded, the application can answer questions without an internet connection.

## Foundry Local Setup Note

During initial setup, Foundry Local produced this Windows error:

```text
[WinError 1114] A dynamic link library (DLL) initialization routine failed.
```

The problem was solved by installing or repairing Microsoft Visual C++ Redistributable 2015–2022 x64 and restarting the computer.

## Current Limitations

- Only `.txt` documents are supported
- Vector comparisons are calculated in Python
- The approach is intended for a small or medium local collection
- The semantic relevance threshold is based on current test data
- Exact artwork matching requires the title to appear in the question
- The accuracy of art answers depends on the correctness of `art_artist.txt`
- Quiz questions currently use a basic repeated format
- The lightweight chat model may produce simpler answers than larger models

## Future Improvements

- Add PDF and DOCX support
- Add tolerance for misspelled artwork titles
- Add automated evaluation tests
- Add response-time measurements
- Improve quiz-question variety
- Add chat history
- Add a dedicated vector database for larger collections
- Validate the complete art-history dataset with museum sources

## Current Status

The project is a working local RAG study assistant with:

- Four local knowledge documents
- 194 stored chunks
- Real Foundry Local embeddings
- Batch embedding generation
- SQLite vector storage
- Cosine similarity
- Exact artwork matching
- Hybrid retrieval
- Dynamic top-k filtering
- Relevance filtering
- Grounded answer generation
- Structured Turkish art answers
- CLI and Streamlit interfaces
- Multiple study modes
- Source information
- Offline-capable local inference



