\# Local RAG Assistant with Microsoft Foundry Local



This project is a local Retrieval-Augmented Generation (RAG) assistant built with Python, SQLite, and Microsoft Foundry Local.



The assistant searches through local document chunks, finds the most relevant information for a user's question, and uses a local Foundry model to generate an answer based on that context.



\## Project Goal



The goal of this project is to build a simple local RAG application that can answer questions from local documents without relying on a cloud-based model.



This project was developed as part of the "Building Your First Local RAG Application with Foundry Local" project.



\## Features



\- Reads local document content

\- Splits documents into chunks

\- Stores chunks in a SQLite database

\- Creates and stores simple embeddings

\- Searches for the most relevant chunk based on the user question

\- Uses Microsoft Foundry Local to generate an answer

\- Shows the source chunk ID and relevance score

\- Runs locally on the computer



\## Technologies Used



\- Python

\- SQLite

\- Microsoft Foundry Local

\- Foundry Local SDK

\- Simple text-based embeddings

\- Git and GitHub



\## Project Structure



```text

rag-assistant/

│

├── documents/

│   └── project\_notes.txt

│

├── answer.py

├── database.py

├── embeddings.py

├── foundry\_answer.py

├── foundry\_test.py

├── main.py

├── search.py

├── rag.db

├── requirements.txt

└── README.md

