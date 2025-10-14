"""
Talk to Your Document - Main FastAPI Application
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
import time
from datetime import datetime

from backend.config import UPLOAD_DIR, API_HOST, API_PORT, SUMMARY_LENGTHS
from backend.models.schemas import (
    QueryRequest, SummarizeRequest, HealthCheck, DocumentStats
)
from backend.services.ocr import OCRService
from backend.services.embedding import EmbeddingService
from backend.services.llm import LLMService
from backend.services.cache import CacheService
from backend.utils.helpers import generate_doc_id, get_timestamp, validate_file_type, get_file_extension
from backend.utils.chunking import calculate_stats

# Initialize FastAPI app
app = FastAPI(
    title="Talk to Your Document API",
    version="2.0.0",
    description="AI-Powered Document Q&A System with Streaming"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ocr_service = OCRService()
embedding_service = EmbeddingService()
llm_service = LLMService()
cache_service = CacheService()

# Global document store
documents_store = {}

# Allowed file types
ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']

@app.get("/", response_model=HealthCheck)
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Talk to Your Document API",
        "version": "2.0.0"
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process PDF or image document"""
    start_time = time.time()
    
    # Validate file type
    if not validate_file_type(file.content_type, ALLOWED_TYPES):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and image files (PNG, JPG, JPEG) are supported"
        )
    
    # Generate document ID
    doc_id = generate_doc_id(file.filename)
    
    # Save file
    file_ext = get_file_extension(file.filename)
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.{file_ext}")
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Extract text based on file type
    try:
        text_chunks, total_pages = ocr_service.extract_text(file_path, file.content_type)
        file_type = "pdf" if file.content_type == 'application/pdf' else "image"
        
        # Calculate stats
        full_text = ' '.join([chunk['content'] for chunk in text_chunks])
        stats = calculate_stats(full_text)
        
        # Check cache before creating embeddings
        if cache_service.check_cache(doc_id):
            print(f"⚡ Using cached embeddings for {doc_id}")
        else:
            # Create embeddings
            embedding_service.create_embeddings(doc_id, text_chunks)
            # Save to cache
            cache_service.save_cache(doc_id, len(text_chunks))
        
        processing_time = time.time() - start_time
        
        # Store document info
        doc_info = {
            "doc_id": doc_id,
            "filename": file.filename,
            "file_type": file_type,
            "file_path": file_path,
            "total_pages": total_pages,
            "total_words": stats['word_count'],
            "total_chars": stats['char_count'],
            "upload_time": get_timestamp(),
            "processing_time": processing_time,
            "chunks": text_chunks
        }
        
        documents_store[doc_id] = doc_info
        
        return {
            "success": True,
            "doc_id": doc_id,
            "stats": {
                "filename": file.filename,
                "file_type": file_type,
                "total_pages": total_pages,
                "total_words": stats['word_count'],
                "total_chars": stats['char_count'],
                "processing_time": round(processing_time, 2)
            }
        }
        
    except Exception as e:
        # Cleanup on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/stream")
async def query_document_stream(request: QueryRequest):
    """
    Ask a question about the document with STREAMING response
    """
    start_time = time.time()
    
    # Check if document exists
    if request.doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Retrieve relevant chunks
    relevant_chunks = embedding_service.retrieve_relevant_chunks(
        request.doc_id,
        request.question,
        top_k=3
    )
    
    if not relevant_chunks:
        async def error_generator():
            yield "I couldn't find relevant information in the document to answer your question."
        return StreamingResponse(error_generator(), media_type="text/plain")
    
    # Build context
    context = "\n\n".join([
        f"[Page {chunk['metadata'].get('page', 'N/A')}]: {chunk['content']}"
        for chunk in relevant_chunks
    ])
    
    # Stream LLM response
    def stream_response():
        try:
            for chunk in llm_service.query_stream(
                request.question,
                context,
                request.chat_history
            ):
                yield chunk
        except Exception as e:
            yield f"\n\n[Error: {str(e)}]"
    
    return StreamingResponse(stream_response(), media_type="text/plain")

@app.post("/query")
async def query_document(request: QueryRequest):
    """
    Ask a question about the document (non-streaming for compatibility)
    """
    start_time = time.time()
    
    # Check if document exists
    if request.doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Retrieve relevant chunks
    relevant_chunks = embedding_service.retrieve_relevant_chunks(
        request.doc_id,
        request.question,
        top_k=3
    )
    
    if not relevant_chunks:
        return {
            "answer": "I couldn't find relevant information in the document to answer your question.",
            "sources": [],
            "response_time": round(time.time() - start_time, 2)
        }
    
    # Build context
    context = "\n\n".join([
        f"[Page {chunk['metadata'].get('page', 'N/A')}]: {chunk['content']}"
        for chunk in relevant_chunks
    ])
    
    # Query LLM (complete response)
    llm_response = llm_service.query_complete(
        request.question,
        context,
        request.chat_history
    )
    
    response_time = time.time() - start_time
    
    return {
        "answer": llm_response['answer'],
        "sources": [
            {
                "page": chunk['metadata'].get('page', 'N/A'),
                "content": chunk['content'][:200] + "...",
                "relevance": round(chunk['relevance'], 2)
            }
            for chunk in relevant_chunks
        ],
        "response_time": round(response_time, 2),
        "tokens_used": llm_response.get('tokens', {})
    }

@app.post("/summarize")
async def summarize_document(request: SummarizeRequest):
    """Generate document summary"""
    start_time = time.time()
    
    # Check if document exists
    if request.doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_info = documents_store[request.doc_id]
    
    # Get full text
    full_text = ' '.join([chunk['content'] for chunk in doc_info['chunks']])
    
    # Limit text length for summarization
    max_chars = SUMMARY_LENGTHS.get(request.length, 4000)
    text_to_summarize = full_text[:max_chars]
    
    # Create summary prompt
    instruction = {
        "length": "in 1 paragraph (5-7 sentences)"
    }
    
    prompt = f"Please summarize the following document {instruction[request.length]}:\n\n{text_to_summarize}"
    
    # Query LLM
    llm_response = llm_service.query_complete(prompt, text_to_summarize, [])
    
    response_time = time.time() - start_time
    
    return {
        "summary": llm_response['answer'],
        "length": request.length,
        "response_time": round(response_time, 2)
    }

@app.get("/document/{doc_id}/stats")
async def get_document_stats(doc_id: str):
    """Get document statistics"""
    if doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_info = documents_store[doc_id]
    
    return {
        "doc_id": doc_id,
        "filename": doc_info['filename'],
        "file_type": doc_info['file_type'],
        "total_pages": doc_info['total_pages'],
        "total_words": doc_info['total_words'],
        "total_chars": doc_info['total_chars'],
        "upload_time": doc_info['upload_time'],
        "processing_time": doc_info['processing_time']
    }

@app.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    return {
        "documents": [
            {
                "doc_id": doc_id,
                "filename": info['filename'],
                "file_type": info['file_type'],
                "upload_time": info['upload_time']
            }
            for doc_id, info in documents_store.items()
        ]
    }

@app.delete("/document/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and its embeddings"""
    if doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_info = documents_store[doc_id]
    
    # Delete file
    if os.path.exists(doc_info['file_path']):
        os.remove(doc_info['file_path'])
    
    # Delete cache
    cache_service.delete_cache(doc_id)
    
    # Delete from ChromaDB
    embedding_service.delete_collection(doc_id)
    
    # Remove from store
    del documents_store[doc_id]
    
    return {"success": True, "message": "Document deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)