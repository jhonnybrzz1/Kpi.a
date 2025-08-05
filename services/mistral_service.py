import os
import requests
import json
from typing import Dict, Any

class MistralService:
    """Serviço para integração com a API Mistral AI"""
    
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY", "default_mistral_key")
        self.base_url = "https://api.mistral.ai/v1/chat/completions"
        self.model = "mistral-large-latest"
    
    def analyze_context(self, initiative_text: str) -> Dict[str, Any]:
        """
        Analisa o contexto da iniciativa usando Mistral AI
        
        Args:
            initiative_text: Texto descrevendo a iniciativa
            
        Returns:
            Dict contendo análise de contexto
        """
        
        prompt = f"""
Você é um especialista em produto com foco em análise de contexto. Sua função é interpretar descrições livres de iniciativas e classificá-las para uso em decisões de produto e sugestão de métricas. 

Extraia e retorne os seguintes campos, com base no texto fornecido:

INICIATIVA: {initiative_text}

1. Tipo da Iniciativa (ex: funcionalidade, campanha, melhoria, experimento)
2. Objetivo Principal do Negócio (ex: aquisição, retenção, receita, engajamento, conversão)
3. Etapa principal do funil AARRR relacionada à iniciativa
4. Complexidade esperada (baixa, média, alta)
5. Áreas de Impacto (ex: tecnologia, vendas, UX, dados, marketing)
6. Frameworks que melhor se aplicam (ex: HEART, AARRR, RICE, JTBD, North Star)
7. Justificativa da classificação

O output deve ser em formato JSON. Evite explicações adicionais fora desse formato.

{{
  "tipo": "",
  "objetivo": "",
  "etapa_funil": "",
  "complexidade": "",
  "area_impacto": [],
  "frameworks_aplicaveis": [],
  "justificativa": ""
}}
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
