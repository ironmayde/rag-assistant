# Local RAG Study Assistant with Microsoft Foundry Local

A local Retrieval-Augmented Generation (RAG) study assistant built with Python, SQLite, Streamlit, and Microsoft Foundry Local.

The application retrieves relevant information from local study notes using semantic vector search and generates source-grounded answers with an on-device language model.

After the required models are downloaded, the assistant can run without an internet connection.

## Project Goal

The goal of this project is to build an offline-capable study assistant that answers questions and creates study materials using the student’s own local documents.

The application demonstrates the three main stages of RAG:

1. Retrieve relevant information from local documents.
2. Augment the model input with the retrieved context.
3. Generate an answer grounded in that context.

## Features

- Reads `.txt` documents from a local folder
- Splits documents into manageable chunks
- Generates real embeddings with Microsoft Foundry Local
- Stores 1024-dimensional vectors in SQLite
- Uses cosine similarity for semantic search
- Retrieves the two most relevant chunks with top-k search
- Rejects unrelated questions using a relevance threshold
- Generates answers with a local chat model
- Applies a grounding check to reduce unsupported output
- Displays source filenames, chunk IDs, and relevance scores
- Supports Ask, Summarize, Quiz, and Flashcards modes
- Includes both CLI and Streamlit interfaces
- Runs locally after the models have been downloaded

## Technologies

- Python 3.12
- SQLite
- Streamlit
- Microsoft Foundry Local
- Foundry Local SDK
- Qwen3 Embedding 0.6B
- Qwen2.5 0.5B
- Cosine similarity
- JSON
- Git and GitHub

## Models

### Embedding model

```text
qwen3-embedding-0.6b
```

This model converts documents and user requests into 1024-dimensional vectors for semantic similarity search.

### Chat model

```text
qwen2.5-0.5b
```

This lightweight local model generates answers from the retrieved context.

## Project Structure

```text
rag-assistant/
│
├── documents/
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

## How the RAG Pipeline Works

### 1. Document ingestion

`ingest.py` reads all `.txt` files from the `documents` folder and divides their contents into smaller chunks.

### 2. Document embeddings

The chunks are sent to `qwen3-embedding-0.6b`.

Each chunk is converted into a 1024-dimensional numerical vector.

### 3. SQLite storage

Each database record contains:

- Chunk ID
- Source filename
- Chunk content
- Embedding vector

Embedding vectors are stored as JSON in `rag.db`.

### 4. Query embedding

The user’s question or topic is converted into a vector using the same embedding model.

### 5. Cosine similarity

The query vector is compared with every stored document vector using cosine similarity.

Values closer to `1.0` indicate greater semantic similarity.

### 6. Top-k retrieval

The results are sorted from highest to lowest similarity.

The application retrieves up to two relevant chunks:

```text
TOP_K = 2
```

### 7. Relevance threshold

The current minimum relevance score is:

```text
0.35
```

Results below this value are rejected.

For an unrelated question, the assistant displays:

```text
I could not find relevant information in the documents.
```

### 8. Grounded generation

The retrieved chunks are combined and sent to the local chat model as context.

The model is instructed to:

- Use only facts explicitly stated in the context
- Avoid outside knowledge
- Avoid invented details
- Avoid unsupported causes, trends, or comparisons

A second grounding check examines the generated answer. Risky answers are replaced with a safer sentence from the retrieved context.

## Installation

Create a virtual environment:

```bat
py -3.12 -m venv .venv
```

Activate the environment:

```bat
.venv\Scripts\activate
```

Install the dependencies:

```bat
pip install -r requirements.txt
```

## Preparing the Documents

Add `.txt` files to the `documents` folder.

Run the ingestion pipeline:

```bat
python ingest.py
```

Example output:

```text
Document ingestion started.
Loaded 5 chunks from commercial_law_notes.txt
Loaded 5 chunks from project_notes.txt
Loaded 5 chunks from statistics_notes.txt

Generating Foundry Local embeddings...

Total chunks saved to database: 15
Document ingestion completed successfully.
```

Run `ingest.py` again whenever a document is added, removed, or changed.

## Running the Streamlit Interface

Start the web interface:

```bat
streamlit run app.py
```

The application normally opens at:

```text
http://localhost:8501
```

The Streamlit interface includes:

- Study mode selection
- Question or topic input
- Generate button
- Document and chunk statistics
- Model information
- Top-k retrieval settings
- Formatted answers and study materials
- Retrieved source information

Stop the application by pressing:

```text
Ctrl + C
```

## Running the CLI Interface

The terminal-based interface is still available:

```bat
python main.py
```

## Study Modes

### Ask

```text
What is RAG?
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

## Example Top-k Result

```text
Sources:
- project_notes.txt | Chunk ID: 38 | Relevance score: 0.7097
- project_notes.txt | Chunk ID: 36 | Relevance score: 0.5408
```

Chunk IDs and relevance scores may change when the database is regenerated.

## Semantic Search Test

Question:

```text
What happens to the distribution of averages when the sample size grows?
```

This question does not directly use the phrase “Central Limit Theorem,” but the system retrieved:

```text
statistics_notes.txt | Chunk ID: 41 | Relevance score: 0.7403
```

This demonstrates semantic retrieval rather than exact keyword matching.

## Unknown Question Test

Question:

```text
Who painted the Mona Lisa?
```

The best similarity score was below the minimum threshold, so the application returned:

```text
I could not find relevant information in the documents.
```

## Final Interface Tests

The following features were successfully tested through Streamlit:

- Ask mode
- Summarize mode
- Quiz mode
- Flashcards mode
- Top-k source display
- Unknown question rejection
- Empty input warning
- Offline operation

## Testing Scripts

Test the local chat model:

```bat
python foundry_test.py
```

Test the embedding model:

```bat
python embedding_test.py
```

The embedding test verifies that the model produces a 1024-dimensional vector.

## Foundry Local Setup Note

During the initial setup, Foundry Local produced this Windows error:

```text
[WinError 1114] A dynamic link library (DLL) initialization routine failed.
```

The problem was solved by installing or repairing Microsoft Visual C++ Redistributable 2015–2022 x64 and restarting the computer.

## Current Limitations

- Only `.txt` files are currently supported
- Cosine similarity is calculated in Python for every stored vector
- The current approach is intended for a small document collection
- The relevance threshold was selected using the current test documents
- The lightweight chat model may produce simpler answers than larger models
- Quiz questions currently use a basic repeated format

## Future Improvements

- Add PDF and DOCX support
- Add automatic evaluation test cases
- Add response-time measurements
- Improve quiz question variety
- Add chat history
- Test with a larger document collection
- Add a dedicated vector database for larger datasets

## Current Status

The project is a working local RAG study assistant with:

- Real Foundry Local embeddings
- SQLite vector storage
- Cosine similarity
- Top-k semantic retrieval
- Relevance filtering
- Grounded answer generation
- CLI and Streamlit interfaces
- Multiple study modes
- Source information
- Offline-capable local inference



