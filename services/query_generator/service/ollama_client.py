import httpx
import asyncio
import json
import logging
from typing import Dict, Any, Optional

from config import settings

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self):
        self.base_url = f"http://{settings.ollama_host}:{settings.ollama_port}"
        self.model = settings.ollama_model
        self.timeout = settings.timeout
    
    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", settings.temperature),
                        "num_predict": kwargs.get("max_tokens", settings.max_tokens),
                        "stop": ["```", "SELECT", "select"]
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("response", "").strip()
                
        except httpx.RequestError as e:
            logger.error(f"Ollama request failed: {str(e)}")
            raise Exception(f"Failed to connect to Ollama: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e.response.status_code}")
            raise Exception(f"Ollama returned error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
    async def check_model_status(self) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                
                models = response.json().get("models", [])
                model_available = any(
                    model.get("name", "").startswith(self.model.split(":")[0]) 
                    for model in models
                )
                
                return {
                    "ollama_status": "running",
                    "model_available": model_available,
                    "model_name": self.model,
                    "available_models": [m.get("name") for m in models]
                }
                
        except httpx.RequestError:
            return {
                "ollama_status": "unreachable",
                "model_available": False,
                "model_name": self.model,
                "error": "Cannot connect to Ollama service"
            }
        except Exception as e:
            return {
                "ollama_status": "error",
                "model_available": False,
                "model_name": self.model,
                "error": str(e)
            }
    
    async def ensure_model_available(self) -> bool:
        try:
            status = await self.check_model_status()
            
            if status["model_available"]:
                return True
            
            logger.info(f"Pulling model {self.model}...")
            async with httpx.AsyncClient(timeout=300) as client:
                payload = {"name": self.model}
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json=payload
                )
                response.raise_for_status()
                
                for _ in range(30):
                    await asyncio.sleep(1)
                    status = await self.check_model_status()
                    if status["model_available"]:
                        logger.info(f"Model {self.model} is now available")
                        return True
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to ensure model availability: {str(e)}")
            return False