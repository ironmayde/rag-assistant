# Local RAG Study Assistant with Microsoft Foundry Local

This project is a local Retrieval-Augmented Generation (RAG) study assistant built with Python, SQLite, and Microsoft Foundry Local.

The assistant searches through local study documents using semantic vector search and generates grounded answers with an on-device language model.

After the required models are downloaded, the application can run locally without sending study documents or questions to a cloud-based model.

## Project Goal

The goal of this project is to build a local study assistant that can answer questions using a collection of course notes.

The application demonstrates the main stages of a RAG pipeline:

1. Retrieve relevant information from local documents.
2. Add the retrieved information to the model’s context.
3. Generate an answer grounded in that context.

## Features

- Reads local `.txt` documents from the `documents` folder
- Splits documents into smaller chunks
- Generates real embeddings with Microsoft Foundry Local
- Uses the `qwen3-embedding-0.6b` embedding model
- Stores 1024-dimensional vectors in SQLite
- Uses cosine similarity for semantic vector search
- Rejects unrelated questions using a minimum relevance threshold
- Uses the `qwen2.5-0.5b` chat model to generate answers
- Applies a grounding check to reduce unsupported model output
- Displays the source filename, chunk ID, and relevance score
- Supports normal questions and multiple study modes
- Runs locally on the user’s computer

## Supported Study Modes

The assistant supports:

- Direct question answering
- `ask`
- `summarize`
- `quiz`
- `flashcard`
- `help`
- `exit`

## Technologies Used

- Python
- SQLite
- Microsoft Foundry Local
- Foundry Local SDK
- Qwen3 Embedding 0.6B
- Qwen2.5 0.5B
- Cosine similarity
- JSON
- Git and GitHub

## Project Structure

```text
rag-assistant/
│
├── documents/
│   ├── commercial_law_notes.txt
│   ├── project_notes.txt
│   └── statistics_notes.txt
│
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

`ingest.py` reads every `.txt` file in the `documents` folder.

The documents are divided into smaller chunks. Long text is split using a maximum word count so that each database entry contains a manageable piece of information.

### 2. Embedding generation

The chunks are sent to the Foundry Local embedding model:

```text
qwen3-embedding-0.6b
```

The model converts each chunk into a 1024-dimensional numerical vector.

### 3. Local vector storage

Each database record contains:

- Chunk ID
- Source filename
- Chunk content
- Embedding vector

The vectors are converted to JSON and stored in the local SQLite database.

### 4. Query embedding

When the user enters a question or topic, the same embedding model converts the request into a 1024-dimensional vector.

### 5. Cosine similarity search

The query vector is compared with every stored chunk vector using cosine similarity.

The chunk with the highest similarity score is selected.

### 6. Relevance threshold

The current minimum relevance score is:

```text
0.35
```

If the best result is below this value, the assistant does not send an unrelated chunk to the chat model.

Instead, it displays:

```text
I could not find relevant information in the documents.
```

### 7. Grounded answer generation

The selected chunk and the user’s question are sent to the local chat model:

```text
qwen2.5-0.5b
```

The system prompt tells the model to use only information explicitly stated in the retrieved context.

A second grounding check examines the generated answer. If the answer contains too much unsupported wording, the assistant replaces it with a safer sentence taken directly from the retrieved context.

## Installation

Create a virtual environment:

```bat
py -3.12 -m venv .venv
```

Activate it on Windows:

```bat
.venv\Scripts\activate
```

Install the required packages:

```bat
pip install -r requirements.txt
```

## Preparing the Documents

Add `.txt` study documents to the `documents` folder.

Then run:

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

The first run may download the embedding model. Once the required model is available locally, it can be reused.

Run `ingest.py` again whenever documents are added, removed, or changed.

## Running the Assistant

Start the application:

```bat
python main.py
```

## Usage Examples

Direct question:

```text
what is rag
```

Ask command:

```text
ask what is limited company
```

Summary:

```text
summarize central limit theorem
```

Quiz:

```text
quiz limited company
```

Flashcards:

```text
flashcard central limit theorem
```

Show help:

```text
help
```

Close the assistant:

```text
exit
```

## Example Answer

```text
Answer:
Short answer:
- RAG means Retrieval-Augmented Generation.

Key points:
- RAG means Retrieval-Augmented Generation.
- It retrieves relevant information, adds it as context, and generates an answer.

Source file: project_notes.txt
Source chunk ID: 38
Relevance score: 0.7097
```

Chunk IDs and relevance scores may change when the database is regenerated.

## Semantic Search Test

The following question does not directly contain the phrase “Central Limit Theorem”:

```text
What happens to the distribution of averages when the sample size grows?
```

The vector search system successfully retrieved the relevant chunk from:

```text
statistics_notes.txt
```

Example relevance score:

```text
0.7403
```

This demonstrates that retrieval is based on semantic similarity rather than only exact keyword matches.

## Unknown Question Test

The following question is not covered by the study documents:

```text
Who painted the Mona Lisa?
```

Its best similarity score was below the minimum threshold, so the assistant returned:

```text
I could not find relevant information in the documents.
```

## Testing Scripts

Test the Foundry Local chat model:

```bat
python foundry_test.py
```

Test the Foundry Local embedding model:

```bat
python embedding_test.py
```

The embedding test displays the vector dimensions and several example values.

## Models Used

### Embedding model

```text
qwen3-embedding-0.6b
```

Purpose:

- Convert documents and questions into numerical vectors
- Support semantic similarity search
- Produce 1024-dimensional embeddings

### Chat model

```text
qwen2.5-0.5b
```

Purpose:

- Generate short study answers from retrieved context
- Run locally with relatively low hardware requirements

## Foundry Local Setup Note

During the initial setup, Foundry Local failed with this Windows error:

```text
[WinError 1114] A dynamic link library (DLL) initialization routine failed.
```

The problem was solved by installing or repairing Microsoft Visual C++ Redistributable 2015–2022 x64 and restarting the computer.

## Current Limitations

- Only `.txt` documents are supported
- All stored vectors are compared in Python, which is suitable for a small document collection
- Only the highest-scoring chunk is currently used as context
- The relevance threshold was selected using the current test collection
- The lightweight chat model may produce simpler answers than larger models
- Quiz and flashcard question variety is currently limited

## Future Improvements

- Retrieve multiple relevant chunks with top-k search
- Add PDF and DOCX document support
- Add a Streamlit web interface
- Add automated evaluation test cases
- Improve quiz and flashcard variety
- Add response-time measurements
- Test the relevance threshold with a larger document collection

## Current Status

The project now works as a local RAG study assistant with:

- Real Foundry Local embeddings
- SQLite vector storage
- Cosine similarity search
- Semantic retrieval
- Relevance filtering
- Grounded local answer generation
- Multiple study modes
- Source information
- Offline-capable local inference



