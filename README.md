# Local RAG Assistant with Microsoft Foundry Local

This project is a local Retrieval-Augmented Generation (RAG) assistant built with Python, SQLite, and Microsoft Foundry Local.

The assistant searches through local document chunks, finds the most relevant information for a user's question, and uses a local Foundry model to generate an answer based on that context.

## Project Goal

The goal of this project is to build a simple local RAG application that can answer questions from local documents without relying on a cloud-based model.

This project was developed as part of the "Building Your First Local RAG Application with Foundry Local" project.

## Features

* Reads local document content
* Splits documents into chunks
* Stores chunks in a SQLite database
* Creates and stores simple embeddings
* Searches for the most relevant chunk based on the user question
* Uses Microsoft Foundry Local to generate an answer
* Shows the source chunk ID and relevance score
* Runs locally on the computer

## Technologies Used

* Python
* SQLite
* Microsoft Foundry Local
* Foundry Local SDK
* Simple text-based embeddings
* Git and GitHub

## Project Structure

```text
rag-assistant/
│
├── documents/
│   └── project_notes.txt
│
├── answer.py
├── database.py
├── embeddings.py
├── foundry_answer.py
├── foundry_test.py
├── ingest.py
├── main.py
├── search.py
├── rag.db
├── requirements.txt
└── README.md
```

## How It Works

1. The local document is divided into smaller chunks.
2. Each chunk is stored in a SQLite database.
3. A simple embedding is created for each chunk.
4. The user asks a question.
5. The question is converted into a simple embedding.
6. The system compares the question embedding with stored chunk embeddings.
7. The most relevant chunk is selected.
8. The selected chunk is sent as context to a Foundry Local model.
9. The model generates an answer based on the provided context.

## Installation

Create and activate a virtual environment:

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Project

First, ingest the documents into the SQLite database:

```bash
python ingest.py
```

Then, run the chatbot:

```bash
python main.py
```

Example question:

```text
what is rag
```

Example output:

```text
Answer:
RAG stands for Retrieval-Augmented Generation.

Source chunk ID: 3
Relevance score: 5
```

## Foundry Local Setup Note

During setup, Foundry Local initially failed with the following error:

```text
[WinError 1114] A dynamic link library (DLL) initialization routine failed.
```

The issue was solved by installing or repairing Microsoft Visual C++ Redistributable 2015-2022 x64 and restarting the computer.

After that, Foundry Local initialized successfully and the model was able to run locally.

## Model Used

The project uses the following Foundry Local model:

```text
qwen2.5-0.5b
```

This model was selected because it is lightweight and suitable for local testing.

## Current Status

The project currently works as a simple local RAG assistant. It retrieves relevant context from local documents and uses Microsoft Foundry Local to generate answers.

## Future Improvements

* Add support for multiple documents
* Improve chunking strategy
* Use real embedding models instead of simple word-frequency embeddings
* Add a better user interface
* Add evaluation metrics for answer quality

