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
Você é um assistente de produto especialista em métricas, OKRs e análise estratégica de funcionalidades. Seu papel é receber um contexto estruturado de uma iniciativa e gerar uma análise completa com:

1. **North Star Metric (NSM):**
   - Nome da NSM
   - Descrição
   - Justificativa da escolha

2. **KPIs Principais:**
   Para cada métrica:
   - Nome
   - Descrição
   - Fórmula de cálculo
   - Frequência recomendada
   - Meta sugerida
   - Área responsável

3. **OKRs Sugeridos:**
   Para cada OKR:
   - Objetivo (O)
   - 3 Key Results (KRs)
   - Prazo sugerido

4. **Frameworks Aplicáveis:**
   Explique quais frameworks de produto se aplicam à iniciativa e como contribuem para análise ou priorização.

5. **Recomendações Técnicas de Medição:**
   - Ferramentas sugeridas (ex: GA4, Mixpanel, Amplitude)
   - Eventos que devem ser configurados
   - Campos recomendados para rastreio
   - Dashboards ou relatórios a serem criados

6. **Riscos e Considerações:**
   Liste até 2 riscos operacionais ou técnicos relevantes.

7. **Próximos Passos:**
   Sugira entre 4 e 6 ações práticas para implementação da medição e adoção dos OKRs.

Formate sua resposta de forma clara e segmentada, com títulos e tabelas. A resposta será exportada para um PDF final.

INICIATIVA: {initiative_text}

CONTEXTO ANALISADO:
- Tipo: {context.get('tipo', 'N/A')}
- Objetivo: {context.get('objetivo', 'N/A')}
- Etapa do funil: {context.get('etapa_funil', 'N/A')}
- Complexidade: {context.get('complexidade', 'N/A')}
- Áreas de impacto: {', '.join(context.get('area_impacto', []))}
- Frameworks aplicáveis: {', '.join(context.get('frameworks_aplicaveis', []))}
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
            
            # Debug: print da resposta
            print(f"OpenAI response: {content}")
            
            parsed_json = json.loads(content)
            print(f"OpenAI parsed successfully: {parsed_json}")
            return parsed_json
            
        except json.JSONDecodeError as e:
            # Retorna estrutura básica em caso de erro de JSON
            return {
                "north_star_metric": {
                    "nome": "Taxa de Sucesso da Iniciativa",
                    "descricao": "Métrica principal para medir o sucesso da iniciativa",
                    "justificativa": "Métrica padrão devido a erro no processamento"
                },
                "kpis": [{
                    "nome": "KPI Principal",
                    "descricao": "Indicador principal de performance",
                    "formula": "A definir",
                    "frequencia_medicao": "semanal",
                    "meta_sugerida": "A definir",
                    "responsavel_area": "Produto"
                }],
                "okrs": [{
                    "objetivo": "Implementar iniciativa com sucesso",
                    "key_results": ["Completar implementação", "Atingir métricas básicas", "Validar com usuários"],
                    "prazo": "trimestral"
                }],
                "frameworks_aplicaveis": [{
                    "nome": "AARRR",
                    "aplicacao": "Framework padrão para análise de funil"
                }],
                "implementacao_medicao": {
                    "ferramentas_sugeridas": ["Google Analytics"],
                    "eventos_configurar": ["Evento principal"],
                    "campos_rastreio": ["Campo básico"],
                    "dashboards": "Dashboard básico de acompanhamento"
                },
                "riscos_metricas": ["Falta de dados", "Complexidade de implementação"],
                "proximos_passos": ["Definir métricas específicas", "Implementar tracking", "Configurar dashboards", "Treinar equipe"]
            }
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
