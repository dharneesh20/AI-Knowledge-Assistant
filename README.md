# AI Knowledge Assistant

> An intelligent document Q&A system — upload your documents, ask questions, get precise AI-powered answers.

---

## Overview

**Personal AI Knowledge Assistant** is a full-stack AI-powered web application that transforms static documents into an interactive knowledge base. Users can upload documents in PDF, DOCX, or TXT format and query their content using natural language. The system uses semantic search via FAISS and generates intelligent, context-aware responses through the Groq LLM API.

This project was developed as part of a hands-on exploration into Retrieval-Augmented Generation (RAG) architecture using real-world tools.

---

## Features

| Feature | Description |
|---|---|
| User Authentication | Secure login and registration system |
| Document Upload | Supports PDF, DOCX, and TXT file formats |
| Text Chunking | Splits documents into semantically meaningful chunks |
| Embedding Generation | Converts text chunks into vector embeddings |
| Semantic Search | Retrieves relevant context using FAISS vector similarity |
| AI Answer Generation | Generates accurate answers using Groq LLM |
| Persistent Storage | Stores document metadata and vectors in SQLite |

---

## System Architecture

```
User Uploads Document
        ↓
  Text Extraction
  (PDF / DOCX / TXT)
        ↓
  Text Chunking
  (Split into segments)
        ↓
  Embedding Generation
  (Sentence Transformers)
        ↓
  Store in FAISS Index
        ↓
  User Submits Query
        ↓
  Similarity Search
  (Top-K relevant chunks)
        ↓
  Groq LLM Response
  (Context-aware answer)
```

---

## Tech Stack

- **Backend:** Python, Django
- **AI / ML:** FAISS, Sentence Transformers, Groq API
- **Database:** SQLite
- **Frontend:** HTML, CSS
- **Document Parsing:** PyMuPDF / python-docx

---

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- A valid [Groq API Key](https://console.groq.com/)

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/dharneesh20/AI-Knowledge-Assistant.git
cd AI-Knowledge-Assistant
```

**2. Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the root directory and add:
```env
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_django_secret_key
DEBUG=True
```

**5. Apply migrations**
```bash
python manage.py migrate
```

**6. Run the development server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

---

## Project Structure

```
AI-Knowledge-Assistant/
│
├── ai_knowledge_assistant/     # Django project settings
├── core/                       # Main application (views, models, logic)
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
├── settings.py                 # Project configuration
└── README.md
```

---

## Usage

1. **Register / Log in** to your account
2. **Upload a document** (PDF, DOCX, or TXT)
3. Wait for the system to **process and index** the document
4. **Type a question** related to the document's content
5. Receive an **AI-generated answer** based on the most relevant sections

---

## Project Duration

**3 Months** — Developed as a solo project from design to deployment.

---

## Author

**Dharneesh**
- GitHub: [@dharneesh20](https://github.com/dharneesh20)

---

## License

This project is licensed under the [MIT License](LICENSE).

---

> *"Turn any document into a conversation."*