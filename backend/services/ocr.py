"""
OCR Service for text extraction from PDFs and images
"""
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from typing import List, Dict, Tuple
from fastapi import HTTPException

class OCRService:
    """Service for extracting text from documents"""
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> Tuple[List[Dict], int]:
        """
        Extract text from PDF using PyMuPDF
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Tuple of (text_chunks, total_pages)
        """
        try:
            doc = fitz.open(file_path)
            text_chunks = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if text.strip():
                    text_chunks.append({
                        "page": page_num + 1,
                        "content": text.strip(),
                        "type": "page"
                    })
            
            total_pages = len(doc)
            doc.close()
            
            if not text_chunks:
                raise HTTPException(
                    status_code=400,
                    detail="No text found in PDF. The file might be image-based or corrupted."
                )
            
            return text_chunks, total_pages
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"PDF extraction failed: {str(e)}"
            )
    
    @staticmethod
    def extract_from_image(file_path: str) -> Tuple[List[Dict], int]:
        """
        Extract text from image using Tesseract OCR
        
        Args:
            file_path: Path to image file
            
        Returns:
            Tuple of (text_chunks, total_pages)
        """
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            
            if not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="No text found in image. The image might be too blurry or contain no text."
                )
            
            chunks = [{
                "page": 1,
                "content": text.strip(),
                "type": "image"
            }]
            
            return chunks, 1
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Image OCR failed: {str(e)}"
            )
    
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> Tuple[List[Dict], int]:
        """
        Extract text based on file type
        
        Args:
            file_path: Path to file
            file_type: MIME type of file
            
        Returns:
            Tuple of (text_chunks, total_pages)
        """
        if file_type == 'application/pdf':
            return OCRService.extract_from_pdf(file_path)
        else:
            return OCRService.extract_from_image(file_path)