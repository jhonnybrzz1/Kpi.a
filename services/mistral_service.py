import os
import requests
import json
from typing import Dict, Any

class MistralService:
    """Serviço para integração com a API Mistral AI"""
    
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY", "default_mistral_key")
        self.base_url = "https://api.mistral.ai/v1/chat/completions"
        self.model = "mistral-large-2512"
    
    def analyze_context(self, initiative_text: str) -> Dict[str, Any]:
        """
        Analisa o contexto da iniciativa usando Mistral AI
        
        Args:
            initiative_text: Texto descrevendo a iniciativa
            
        Returns:
            Dict contendo análise de contexto
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
                
                # Tenta fazer parse do JSON
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Se falhar, extrai JSON do texto
                    return self._extract_json_from_text(content)
            
            else:
                raise Exception(f"Erro na API Mistral: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro de conexão com Mistral: {str(e)}")
        except Exception as e:
            raise Exception(f"Erro no serviço Mistral: {str(e)}")
    
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
