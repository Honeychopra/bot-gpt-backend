# app/services/llm_service.py
import os
from groq import Groq
from typing import List, Dict
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class LLMService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"  # or "mixtral-8x7b-32768"
        self.max_tokens = 1024
    
    async def generate_response(self, messages: List[Dict[str, str]]) -> dict:
        """
        Generate response from LLM
        
        Args:
            messages: List of dicts with 'role' and 'content'
                     [{"role": "user", "content": "Hello"}]
        
        Returns:
            dict with 'content' and 'tokens'
        """
        try:
            # Add system message
            full_messages = [
                {"role": "system", "content": "You are a helpful assistant."}
            ] + messages
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            # Extract response
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens
            
            return {
                "content": content,
                "tokens": tokens
            }
            
        except Exception as e:
            print(f"LLM API Error: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")