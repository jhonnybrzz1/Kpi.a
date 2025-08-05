import os
import json
from openai import OpenAI
from typing import Dict, Any, List

class OpenAIService:
    """Serviço para integração com OpenAI GPT-4"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "default_openai_key")
        self.client = OpenAI(api_key=self.api_key)
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
    
    def generate_metrics(self, initiative_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera métricas, KPIs e OKRs baseados na iniciativa e contexto
        
        Args:
            initiative_text: Texto da iniciativa
            context: Contexto analisado pelo Mistral
            
        Returns:
            Dict com métricas, KPIs e OKRs sugeridos
        """
        
        prompt = f"""
Você é um assistente de produto especialista em métricas, OKRs e análise estratégica de funcionalidades. Seu papel é receber um contexto estruturado de uma iniciativa e gerar uma análise completa.

INICIATIVA: {initiative_text}

CONTEXTO ANALISADO:
- Tipo: {context.get('tipo', 'N/A')}
- Objetivo: {context.get('objetivo', 'N/A')}
- Etapa do funil: {context.get('etapa_funil', 'N/A')}
- Complexidade: {context.get('complexidade', 'N/A')}
- Áreas de impacto: {', '.join(context.get('area_impacto', []))}
- Frameworks aplicáveis: {', '.join(context.get('frameworks_aplicaveis', []))}

Gere uma análise completa em JSON com:

{{
  "north_star_metric": {{
    "nome": "Nome da NSM",
    "descricao": "Descrição detalhada",
    "justificativa": "Justificativa da escolha"
  }},
  "kpis": [
    {{
      "nome": "Nome do KPI",
      "descricao": "Descrição detalhada",
      "formula": "Fórmula de cálculo",
      "frequencia_medicao": "Frequência recomendada",
      "meta_sugerida": "Meta sugerida",
      "responsavel_area": "Área responsável"
    }}
  ],
  "okrs": [
    {{
      "objetivo": "Objetivo (O)",
      "key_results": [
        "Key Result 1 quantificado",
        "Key Result 2 quantificado", 
        "Key Result 3 quantificado"
      ],
      "prazo": "Prazo sugerido"
    }}
  ],
  "frameworks_aplicaveis": [
    {{
      "nome": "Nome do framework",
      "aplicacao": "Como aplicar e contribuir para análise"
    }}
  ],
  "implementacao_medicao": {{
    "ferramentas_sugeridas": ["GA4", "Mixpanel", "Amplitude"],
    "eventos_configurar": ["Lista de eventos a configurar"],
    "campos_rastreio": ["Campos recomendados para rastreio"],
    "dashboards": "Dashboards ou relatórios a serem criados"
  }},
  "riscos_metricas": [
    "Risco operacional ou técnico 1",
    "Risco operacional ou técnico 2"
  ],
  "proximos_passos": [
    "Ação prática 1 para implementação",
    "Ação prática 2 para medição",
    "Ação prática 3 para adoção dos OKRs",
    "Ação prática 4"
  ]
}}

Formate sua resposta de forma clara e segmentada. As métricas devem ser SMART e práticas.
Responda APENAS com o JSON válido, sem texto adicional.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em métricas de produto e análise de dados. "
                                 "Responda sempre em JSON válido conforme solicitado."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.4,
                max_tokens=2500
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise Exception("Resposta vazia do OpenAI")
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            raise Exception(f"Erro ao decodificar resposta JSON do OpenAI: {str(e)}")
        except Exception as e:
            raise Exception(f"Erro no serviço OpenAI: {str(e)}")
    
    def generate_executive_summary(self, initiative_text: str, context: Dict[str, Any], 
                                 metrics: Dict[str, Any]) -> str:
        """
        Gera um resumo executivo da análise
        
        Args:
            initiative_text: Texto da iniciativa
            context: Contexto analisado
            metrics: Métricas geradas
            
        Returns:
            String com resumo executivo
        """
        
        prompt = f"""
Com base na iniciativa e análises realizadas, escreva um resumo executivo profissional 
que explique de forma clara e concisa:

1. O que é a iniciativa
2. Por que as métricas escolhidas são relevantes
3. Como implementar a medição
4. Benefícios esperados

INICIATIVA: {initiative_text}
CONTEXTO: {json.dumps(context, indent=2, ensure_ascii=False)}
MÉTRICAS: {json.dumps(metrics, indent=2, ensure_ascii=False)}

O resumo deve ter entre 200-400 palavras, ser profissional e focado em resultados de negócio.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um consultor de negócios especializado em redação executiva."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=600
            )
            
            content = response.choices[0].message.content
            return content if content is not None else "Não foi possível gerar o resumo executivo."
            
        except Exception as e:
            return f"Não foi possível gerar o resumo executivo. Erro: {str(e)}"
