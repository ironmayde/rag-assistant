# Local RAG Study Assistant with Microsoft Foundry Local

This project is a local Retrieval-Augmented Generation (RAG) study assistant built with Python, SQLite, and Microsoft Foundry Local.

The assistant searches through local document chunks, finds the most relevant information for a user's request, and uses a local Foundry model to generate grounded study answers based on that context.

## Project Goal

The goal of this project is to build a simple local RAG application that can help students study from their own local notes without relying on a cloud-based model.

This project was developed as part of the "Building Your First Local RAG Application with Foundry Local" project.

## Features

* Reads local `.txt` documents from the `documents` folder
* Splits documents into chunks
* Stores chunks, source filenames, and embeddings in a SQLite database
* Searches for the most relevant chunk based on the user request
* Uses Microsoft Foundry Local to generate answers
* Shows the source file, source chunk ID, and relevance score
* Supports direct questions
* Supports study commands:

  * ask a question
  * summarize a topic
  * generate a quiz
  * generate flashcards
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
│   ├── project_notes.txt
│   ├── statistics_notes.txt
│   └── commercial_law_notes.txt
│
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

1. `.txt` files are added to the `documents` folder.
2. `ingest.py` reads the documents.
3. The text is split into smaller chunks.
4. Each chunk is stored in a SQLite database with its source filename.
5. A simple embedding is created and stored for each chunk.
6. The user enters a question or a study command.
7. The system finds the most relevant chunk.
8. The selected chunk is sent as context to a Foundry Local model.
9. The assistant generates a grounded study response.
10. The response includes the source file, chunk ID, and relevance score.

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

## Preparing the Documents

Before running the chatbot, ingest the documents into the SQLite database:

```bash
python ingest.py
```

Example output:

```text
Document ingestion started.
Loaded 5 chunks from commercial_law_notes.txt
Loaded 5 chunks from project_notes.txt
Loaded 5 chunks from statistics_notes.txt

Total chunks saved to database: 15
Document ingestion completed successfully.
```

## Running the Study Assistant

Run the chatbot:

```bash
python main.py
```

The assistant supports direct questions and study commands.

## Supported Inputs

Direct question:

```text
what is rag
```

Ask command:

```text
ask what is rag
```

Summarize command:

```text
summarize central limit theorem
```

Quiz command:

```text
quiz limited company
```

Flashcard command:

```text
flashcard central limit theorem
```

Other commands:

```text
help
exit
```

## Example Answer Output

```text
Answer:
Short answer:
- RAG stands for Retrieval-Augmented Generation.

Key points:
- RAG means Retrieval-Augmented Generation.
- It retrieves relevant information, adds it as context, and generates an answer.

Exam note:
- Remember this topic from project_notes.txt; it may be useful for definition, explanation, or short-answer exam questions.

Grounding note:
- The model answer passed the context-grounding check.

Source file: project_notes.txt
Source chunk ID: 8
Relevance score: 5
```

## Example Summary Output

```text
Summary:
- Central Limit Theorem says that when the sample size is large enough, the sampling distribution of the sample mean becomes approximately normal.

Source file: statistics_notes.txt
Source chunk ID: 11
Relevance score: 3
```

## Example Quiz Output

```text
Quiz:
Question 1: What should you remember about this topic?
Answer 1: A limited company has legal personality.

Question 2: What should you remember about this topic?
Answer 2: Legal personality is gained by registration in the trade registry.

Source file: commercial_law_notes.txt
Source chunk ID: 1
Relevance score: 2
```

## Example Flashcard Output

```text
Flashcards:
Card 1
Q: What should you remember?
A: Central Limit Theorem says that when the sample size is large enough, the sampling distribution of the sample mean becomes approximately normal.

Source file: statistics_notes.txt
Source chunk ID: 11
Relevance score: 3
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

The project currently works as a local RAG study assistant. It can retrieve relevant context from multiple local notes and support direct questions, question answering, summarization, quiz generation, and flashcard generation.

## Future Improvements

* Add support for more file types such as PDF and DOCX
* Improve the retrieval system with real embedding models
* Improve quiz question variety
* Add a Streamlit web interface
* Add evaluation metrics for answer quality



