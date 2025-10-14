"""
LLM Service for interacting with LM Studio
Enhanced for concise, emoji-rich responses
"""
import requests
import json
from typing import List, Dict, Generator
from fastapi import HTTPException
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    LM_STUDIO_URL,
    LM_STUDIO_TIMEOUT,
    DEFAULT_TEMPERATURE,
    MAX_TOKENS,
    CHAT_HISTORY_LIMIT
)

class LLMService:
    """Service for LLM interactions"""
    
    @staticmethod
    def build_messages(question: str, context: str, chat_history: List[Dict] = [], is_summary: bool = False) -> List[Dict]:
        """
        Build messages array for LLM with few-shot examples
        """
        if is_summary:
            system_prompt = """You are a concise document summarizer. Keep summaries under 100 words."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                # Few-shot example
                {"role": "user", "content": "Summarize this job posting: [long job description text]"},
                {"role": "assistant", "content": """Job posting for Junior UI/UX Designer! 🎨

**Overview**: Remote position across Europe, $1,100/month

**Requirements**:
• 0-2 years experience
• Figma, Adobe XD, Miro, Canva
• Portfolio + prototyping skills

**Benefits**: Flexible hours, $150 tool budget, career growth 🚀"""},
                # Actual request
                {"role": "user", "content": f"Summarize this document concisely:\n{context}"}
            ]
        else:
            system_prompt = """You are a concise AI assistant. Maximum 5 sentences or 5 bullet points."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                # Few-shot example 1
                {"role": "user", "content": "What is this document about? [job posting text]"},
                {"role": "assistant", "content": """Junior UI/UX Designer job posting! 🎨

**Key info**:
• 💰 $1,100/month
• 📍 Remote (Europe)
• 🛠️ Figma, Adobe XD, Miro
• ⏰ 0-2 years experience"""},
                # Few-shot example 2
                {"role": "user", "content": "What are the requirements?"},
                {"role": "assistant", "content": """**Requirements**:
✅ 0-2 years UI/UX experience
✅ Strong portfolio
✅ Usability/accessibility knowledge
✅ Basic prototyping skills"""}
            ]
            
            # Add chat history
            for msg in chat_history[-CHAT_HISTORY_LIMIT:]:
                messages.append(msg)
            
            # Add actual question
            messages.append({
                "role": "user", 
                "content": f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer concisely with emojis:"
            })
        
        return messages
    
    @staticmethod
    def query_stream(prompt: str, context: str, chat_history: List[Dict] = []) -> Generator[str, None, None]:
        """
        Query LM Studio with streaming response
        """
        try:
            messages = LLMService.build_messages(prompt, context, chat_history, is_summary=False)
            
            response = requests.post(
                LM_STUDIO_URL,
                json={
                    "messages": messages,
                    "temperature": 0.5,  # Lower for more focused responses
                    "max_tokens": 150,  # Even shorter - force brevity!
                    "stream": True,
                    "stop": ["\n\n\n", "In summary", "To summarize"]  # Stop verbose patterns
                },
                timeout=LM_STUDIO_TIMEOUT,
                stream=True
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"LM Studio error: {response.text}"
                )
            
            # Stream the response
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            json_data = json.loads(data)
                            if 'choices' in json_data and len(json_data['choices']) > 0:
                                delta = json_data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=503,
                detail=f"LM Studio connection failed: {str(e)}. Make sure LM Studio is running on http://localhost:1234"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"LLM query failed: {str(e)}"
            )
    
    @staticmethod
    def query_complete(prompt: str, context: str, chat_history: List[Dict] = []) -> Dict:
        """
        Query LM Studio with complete response (for summarization)
        """
        try:
            messages = LLMService.build_messages(prompt, context, chat_history, is_summary=True)
            
            response = requests.post(
                LM_STUDIO_URL,
                json={
                    "messages": messages,
                    "temperature": 0.3,  # Even lower for focused summaries
                    "max_tokens": 150,  # Very short for concise summaries
                    "stream": False,
                    "stop": ["\n\n\n", "In conclusion"]  # Stop verbose patterns
                },
                timeout=LM_STUDIO_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "answer": result['choices'][0]['message']['content'],
                    "model": result.get('model', 'unknown'),
                    "tokens": result.get('usage', {})
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"LM Studio error: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=503,
                detail=f"LM Studio connection failed: {str(e)}. Make sure LM Studio is running on http://localhost:1234"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"LLM query failed: {str(e)}"
            )
        
        