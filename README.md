--- 
<div align="center"> 
    <h1>🧠 Talk to Your Document</h1> 
    
![Project Banner](https://img.shields.io/badge/AI-Powered-ff69b4?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)

**Upload documents, extract text with OCR, and chat with AI about your content**

</div>

---

## 🎯 Overview

**Talk to Your Document** is an intelligent document analysis system that combines OCR, embeddings-based retrieval (RAG), and Large Language Models to enable natural conversations about your documents. Upload a PDF or image, and ask questions as if you're talking to someone who has read the entire document.

### Why This Project?

This project was built as to demonstrate:
- End-to-end AI engineering skills
- Full-stack development capabilities
- Production-ready code architecture
- Modern UI/UX design principles

---

## ✨ Features

### Core Functionality
- 📤 **Document Upload** - Drag & drop or click to upload PDF/images
- 🔍 **OCR Text Extraction** - PyMuPDF for PDFs, Tesseract for images  
- 🧩 **Smart Text Chunking** - Overlapping chunks for context preservation
- 🤖 **AI-Powered Q&A** - Natural language queries with streaming responses
- 🎯 **Semantic Search** - FAISS vector similarity for relevant context retrieval
- 💬 **Conversational Memory** - Multi-turn conversations with chat history

---

## 🎥 Demo

### Live Demo Video
https://github.com/user-attachments/assets/09c7bbe7-f527-4ad9-8c54-a352558370f1


### Screenshots

<details>
<summary>📸 Click to view screenshots</summary>

#### Upload Interface
<img width="2879" height="1620" alt="Screenshot 2025-10-14 214847" src="https://github.com/user-attachments/assets/09d8c03d-fedd-4ddb-8aa9-c46c1566b3a4" />

#### Document Preview & Chat
<img width="2879" height="1625" alt="Screenshot 2025-10-14 215148" src="https://github.com/user-attachments/assets/b8e21aba-90ce-429d-a432-99eae46cd9b4" />

#### Summary Generation
<img width="2879" height="1618" alt="Screenshot 2025-10-14 220924" src="https://github.com/user-attachments/assets/ddf799ca-8abe-4449-9fcb-06dc8a83d91b" />

</details>

---

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

**Python 3.10+** - [Download](https://www.python.org/downloads/)

**Tesseract OCR** - Required for image text extraction
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
```

**LM Studio** (Optional but recommended) - [Download](https://lmstudio.ai/)
- Load any model (e.g., Llama 3.2, Mistral, Phi-3)
- Start server on `http://localhost:1234`

---

### Installation

**1️⃣ Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/talk-to-document.git
cd talk-to-document
```

**2️⃣ Create virtual environment**
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

**3️⃣ Install dependencies**
```bash
pip install -r requirements.txt
```

**4️⃣ Download embedding model**
```bash
# This happens automatically on first run
# Downloads sentence-transformers/all-MiniLM-L6-v2 (~90MB)
```

**5️⃣ Set up LM Studio** (Optional, but Recommended)
- Download LM Studio from https://lmstudio.ai/
- Download a model (recommended: Llama-3.2-3B-Instruct)
- Start local server on port 1234
- Your backend will automatically connect

**6️⃣ Start the backend**
```bash
cd backend
python app.py
# Server starts on http://localhost:8000
```

**7️⃣ Start the frontend**
```bash
# Open a new terminal
cd frontend
# Serve with any static server, e.g.:
python -m http.server 3000

# Or use Live Server extension in VS Code
```

**8️⃣ Open in browser**
```
http://localhost:3000
```

---

## 🏗️ Architecture

### 🧑🏻‍🎨 System Design
![system flow diagram](https://github.com/user-attachments/assets/d56e5ef1-6653-46f9-8a78-4a6fcd82d6b8)

### 🔄 Data Flow 

1. **Upload** → User uploads PDF/image → Saved to `/uploads`
2. **Extraction** → OCR extracts text → Chunked with overlap
3. **Embedding** → Chunks converted to vectors → Stored in FAISS
4. **Query** → User asks question → Semantic search retrieves relevant chunks
5. **Generation** → Context + Question → LLM generates answer
6. **Display** → Answer streams character-by-character to UI

---

## 🛠️ Technologies Used

### Backend
| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **FastAPI** | Web framework | Modern, async, automatic API docs |
| **PyMuPDF** | PDF text extraction | Fast, accurate, native Python |
| **Tesseract** | Image OCR | Industry standard, multilingual |
| **Sentence Transformers** | Text embeddings | SOTA semantic similarity |
| **FAISS** | Vector search | Blazing fast, production-ready |
| **LM Studio** | Local LLM inference | Privacy, no API costs |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Vanilla JavaScript** | Core functionality |
| **CSS3** | Modern styling with gradients |
| **HTML5** | Semantic markup |

### Why These Choices?

**FAISS over ChromaDB**: Simpler deployment, no separate database service needed, faster for small-to-medium datasets.

**Local LLM over API**: Privacy-first, no API costs, works offline, demonstrates understanding of model deployment.

**Vanilla JS over React**: Keeps bundle size small, demonstrates core web skills, easier for reviewers to understand.

---

## 📁 Project Structure

```
talk-to-document/
├── backend/
│   ├── app.py                 # Main FastAPI application
│   ├── config.py              # Configuration settings
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   ├── ocr.py            # Text extraction service
│   │   ├── embedding.py      # FAISS vector service
│   │   ├── llm.py            # LM Studio integration
│   │   └── cache.py          # Caching service
│   └── utils/
│       ├── chunking.py       # Text chunking utilities
│       └── helpers.py        # Helper functions
├── frontend/
│   ├── index.html            # Main HTML file
│   ├── css/
│   │   └── styles.css        # Styling
│   └── js/
│       └── app.js            # Frontend logic
├── uploads/                   # Uploaded documents
├── cache/                     # Embedding cache
├── chroma_db/                 # FAISS indexes
├── requirements.txt           # Python dependencies
├── README.md                  # README file
└── DOCUMENTATION.md           # Process documentation
```

---

## 📊 Performance Metrics

| Operation | Time (avg) | Notes |
|-----------|------------|-------|
| PDF Upload (10 pages) | 5s | Includes OCR + embedding |
| Image Upload | 4s | Depends on image size |
| Query Response | 30-50s | Streaming starts at 10s |
| Summary Generation | 40-60s | For ~2000 words |
| Semantic Search | <100ms | FAISS is fast |

---

## 🐛 Known Issues

- **LM Studio Required**: Currently needs local LM Studio running. Future version will support cloud APIs as fallback.
- **Large PDFs**: Files >50MB may take longer to process.

---

## 🧪 Manual Tests Performed

| Test Case | Input | Expected Output | Result |
|-----------|-------|----------------|--------|
| PDF Upload | 10-page research paper | Text extracted, 10 pages | ✅ Pass |
| Image Upload | Photo of handwritten note | Text recognized | ✅ Pass |
| Query Response | "What is this about?" | Relevant answer | ✅ Pass |
| Summarization | Full document | Concise 1-paragraph summary | ✅ Pass |
| Chat History | Multiple questions | Persisted in localStorage | ✅ Pass |
| Export Chat | 10 message exchanges | Downloaded as .txt | ✅ Pass |
| Caching | Re-upload same file | 10x faster processing | ✅ Pass |

---
## 🎯 Conclusion

This project demonstrates a complete AI engineering pipeline from document ingestion to intelligent question-answering. By combining OCR, semantic search with FAISS, and LLM integration, it showcases:

- **End-to-End AI Implementation**: From text extraction to conversational AI
- **Production-Ready Architecture**: Clean code, error handling, and performance optimization
- **Modern Tech Stack**: FastAPI, FAISS, Sentence Transformers, and local LLM deployment
- **Full-Stack Development**: Both frontend and backend implementation with streaming responses

The application successfully handles real-world document analysis tasks while maintaining privacy through local LLM deployment and offering a smooth user experience with real-time streaming.

---
<div align="center">

⭐ **If you found this project interesting, please star this repo!** ⭐


**Mohammed Tawfiq**  
[tawfiqmohammed707@gmail.com](mailto:tawfiqmohammed707@gmail.com)  
[GitHub](https://github.com/tawfiqmohammed) | [LinkedIn](linkedin.com/in/tawfiq-mohammed/)

</div>
