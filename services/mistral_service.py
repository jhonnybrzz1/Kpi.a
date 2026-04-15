import os
import requests
import json
import time
import logging
from typing import Dict, Any
from functools import wraps

# Configure module logger
logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries=3, base_delay=1):
    """Decorator to retry function calls with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error("Failed after %d attempts: %s", max_retries, str(e))
                        raise
                    delay = base_delay * (2 ** attempt)
                    logger.warning("Attempt %d failed, retrying in %ds: %s", attempt + 1, delay, str(e))
                    time.sleep(delay)
        return wrapper
    return decorator

class MistralService:
    """Service for Mistral AI API integration"""

    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError(
                "MISTRAL_API_KEY not configured. "
                "Please set the environment variable before using this service."
            )
        self.base_url = "https://api.mistral.ai/v1/chat/completions"
        self.model = "mistral-large-2512"
        logger.info("MistralService initialized with model: %s", self.model)

    @retry_with_backoff(max_retries=3, base_delay=2)
    def analyze_context(self, initiative_text: str) -> Dict[str, Any]:
        """
        Analyzes initiative context using Mistral AI

        Args:
            initiative_text: Text describing the initiative

        Returns:
            Dict containing context analysis
        """
        
        prompt = f"""
Você é um especialista em análise de projetos e métricas de negócio. 
Analise a seguinte iniciativa e classifique-a nos critérios abaixo.

INICIATIVA: {initiative_text}

Forneça uma análise estruturada em JSON com os seguintes campos:

1. "tipo": Classifique como uma das opções: "funcionalidade", "processo", "produto", "estrategia"
2. "objetivo": Classifique o objetivo principal como: "aquisicao", "ativacao", "retencao", "receita", "engajamento"  
3. "etapa_funil": Identifique a etapa do funil AARRR: "aquisicao", "ativacao", "retencao", "receita", "referencia"
4. "complexidade": Avalie como: "baixa", "media", "alta"
5. "area_impacto": Lista de áreas impactadas (ex: ["vendas", "operacoes", "tecnologia"])
6. "justificativa": Texto explicando a classificação e contexto identificado
7. "palavras_chave": Lista das palavras-chave mais relevantes da iniciativa

Responda APENAS com o JSON válido, sem texto adicional.
        """
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }

            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # Try to parse JSON
                try:
                    data = json.loads(content)
                    logger.info("Successfully analyzed initiative context")
                    return data
                except json.JSONDecodeError:
                    # If fails, extract JSON from text
                    logger.warning("JSON parse failed, extracting from text")
                    return self._extract_json_from_text(content)

            else:
                raise Exception(f"Mistral API error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error with Mistral: {str(e)}")
        except Exception as e:
            raise Exception(f"Error in Mistral service: {str(e)}")
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extrai JSON de texto que pode conter outros caracteres"""
        try:
            # Procura por { e } para extrair JSON
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start != -1 and end != 0:
                json_str = text[start:end]
                return json.loads(json_str)
            
            # Fallback: retorna estrutura padrão
            return {
                "tipo": "funcionalidade",
                "objetivo": "operacao",
                "etapa_funil": "ativacao",
                "complexidade": "media",
                "area_impacto": ["tecnologia"],
                "justificativa": "Análise automática baseada no texto fornecido.",
                "palavras_chave": ["iniciativa", "projeto", "implementação"]
            }
            
        except Exception:
            # Retorna estrutura padrão em caso de erro
            return {
                "tipo": "funcionalidade",
                "objetivo": "operacao",
                "etapa_funil": "ativacao",
                "complexidade": "media",
                "area_impacto": ["tecnologia"],
                "justificativa": "Não foi possível processar a análise de contexto.",
                "palavras_chave": ["iniciativa", "projeto"]
            }
