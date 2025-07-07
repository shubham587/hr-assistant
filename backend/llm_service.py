import requests
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # LM Studio default endpoint
        self.base_url = "http://localhost:1234/v1"
        self.model_name = "mistral-7b-instruct-v0.1"
        
    def is_healthy(self) -> bool:
        """Check if LM Studio is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, query: str, context_chunks: List[Dict]) -> str:
        """Generate response using LM Studio"""
        try:
            # Prepare context from chunks
            context = self._prepare_context(context_chunks)
            
            # Create system prompt
            system_prompt = self._create_system_prompt()
            
            # Create user prompt with context
            user_prompt = self._create_user_prompt(query, context)
            
            # Call LM Studio API
            response = self._call_lm_studio(system_prompt, user_prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I apologize, but I'm having trouble processing your request right now. Please try again later."
    
    def _prepare_context(self, context_chunks: List[Dict]) -> str:
        """Prepare context string from retrieved chunks"""
        if not context_chunks:
            return "No relevant information found in the documents."
        
        context_parts = []
        for i, chunk in enumerate(context_chunks[:3]):  # Use top 3 chunks
            document = chunk.get('metadata', {}).get('document', 'Unknown')
            text = chunk.get('text', '')
            
            context_parts.append(f"Source {i+1} ({document}):\n{text}")
        
        return "\n\n".join(context_parts)
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for the HR assistant"""
        return """You are a helpful HR assistant that answers employee questions based on company documents. 

Your role:
- Answer questions about HR policies, benefits, leave, and employment terms
- Use only the information provided in the context
- Be clear, concise, and professional
- If you don't have enough information, say so honestly
- Always cite the source document when possible

Guidelines:
- Keep responses under 200 words
- Use bullet points for lists
- Be empathetic and helpful
- If the question is not HR-related, politely redirect to appropriate resources"""
    
    def _create_user_prompt(self, query: str, context: str) -> str:
        """Create user prompt with query and context"""
        return f"""Context from HR documents:
{context}

Employee question: {query}

Please provide a helpful answer based on the context above. If the context doesn't contain relevant information, please say so."""
    
    def _call_lm_studio(self, system_prompt: str, user_prompt: str) -> str:
        """Make API call to LM Studio"""
        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 300,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                logger.error(f"LM Studio API error: {response.status_code} - {response.text}")
                return "I'm having trouble connecting to the AI service. Please try again later."
                
        except requests.exceptions.Timeout:
            logger.error("LM Studio API timeout")
            return "The request is taking too long. Please try again with a simpler question."
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to LM Studio")
            return "Cannot connect to the AI service. Please make sure LM Studio is running."
        except Exception as e:
            logger.error(f"LM Studio API error: {str(e)}")
            return "I'm experiencing technical difficulties. Please try again later."
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from LM Studio"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=10)
            if response.status_code == 200:
                models = response.json()
                return [model["id"] for model in models["data"]]
            return []
        except:
            return []
    
    def test_connection(self) -> Dict:
        """Test connection to LM Studio and return status"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            if response.status_code == 200:
                models = self.get_available_models()
                return {
                    "status": "connected",
                    "models": models,
                    "endpoint": self.base_url
                }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}",
                    "endpoint": self.base_url
                }
        except requests.exceptions.ConnectionError:
            return {
                "status": "disconnected",
                "message": "Cannot connect to LM Studio. Make sure it's running on localhost:1234",
                "endpoint": self.base_url
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "endpoint": self.base_url
            } 