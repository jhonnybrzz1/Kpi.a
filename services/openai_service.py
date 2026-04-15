import os
import json
from openai import OpenAI
from typing import Dict, Any, List

class OpenAIService:
    """Serviço para integração com OpenAI GPT-4"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "default_openai_key")
        self.client = OpenAI(api_key=self.api_key)
        # Updated to use gpt-4o-mini for better stability and cost efficiency
        # gpt-4o-mini supports structured outputs and is more reliable
        self.model = "gpt-4o-mini"
    
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
Você é um especialista em métricas de produto, KPIs e OKRs. Com base na iniciativa e contexto fornecidos, 
gere uma análise completa de métricas.

INICIATIVA: {initiative_text}

CONTEXTO ANALISADO:
- Tipo: {context.get('tipo', 'N/A')}
- Objetivo: {context.get('objetivo', 'N/A')}
- Etapa do funil: {context.get('etapa_funil', 'N/A')}
- Complexidade: {context.get('complexidade', 'N/A')}
- Áreas de impacto: {', '.join(context.get('area_impacto', []))}

Gere uma resposta em JSON com a seguinte estrutura:

{{
  "north_star_metric": {{
    "nome": "Nome da métrica principal",
    "descricao": "Descrição detalhada da North Star Metric",
    "justificativa": "Por que esta é a métrica mais importante"
  }},
  "kpis": [
    {{
      "nome": "Nome do KPI",
      "descricao": "Descrição do KPI",
      "formula": "Fórmula de cálculo",
      "frequencia_medicao": "diária/semanal/mensal",
      "meta_sugerida": "Meta numérica sugerida",
      "responsavel_area": "Área responsável pela medição"
    }}
  ],
  "okrs": [
    {{
      "objetivo": "Objetivo claro e inspirador",
      "key_results": [
        "Key Result 1 com meta quantificada",
        "Key Result 2 com meta quantificada",
        "Key Result 3 com meta quantificada"
      ],
      "prazo": "Prazo sugerido (ex: trimestral)"
    }}
  ],
  "frameworks_aplicaveis": [
    {{
      "nome": "Nome do framework (ex: HEART, RICE, AARRR)",
      "aplicacao": "Como aplicar este framework na iniciativa"
    }}
  ],
  "implementacao_medicao": {{
    "ferramentas_sugeridas": ["Lista de ferramentas para medição"],
    "setup_tracking": "Instruções para configurar o tracking",
    "dashboards": "Sugestões de dashboards e visualizações"
  }},
  "riscos_metricas": [
    "Risco 1 relacionado às métricas",
    "Risco 2 que pode afetar a medição"
  ]
}}

Seja específico e prático. As métricas devem ser SMART (Específicas, Mensuráveis, Atingíveis, Relevantes, Temporais).
Inclua pelo menos 3-5 KPIs principais e 1-2 OKRs completos.

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
            
            # Limpar o conteúdo removendo possíveis blocos de código markdown
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
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
