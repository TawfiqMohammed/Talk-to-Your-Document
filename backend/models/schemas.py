"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    doc_id: str
    question: str
    chat_history: Optional[List[Dict[str, str]]] = []

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    response_time: float
    tokens_used: Optional[Dict[str, int]] = {}

class SummarizeRequest(BaseModel):
    doc_id: str
    length: str = "medium"

class SummarizeResponse(BaseModel):
    summary: str
    length: str
    response_time: float

class DocumentStats(BaseModel):
    doc_id: str
    filename: str
    file_type: str
    total_pages: int
    total_words: int
    total_chars: int
    upload_time: str
    processing_time: float

class UploadResponse(BaseModel):
    success: bool
    doc_id: str
    stats: DocumentStats

class HealthCheck(BaseModel):
    status: str
    service: str
    version: str

class ErrorResponse(BaseModel):
    detail: str
    error_type: str