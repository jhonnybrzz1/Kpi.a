# 📋 RELATÓRIO TÉCNICO - MetricFlow AI

> **Data:** 15/04/2026  
> **Autor:** Engenheiro de Software Sênior / Arquiteto de IA  
> **Repositório:** https://github.com/jhonnybrzz1/Kpi.a  
> **Versão:** 1.0

---

## 1. RESUMO EXECUTIVO

O **MetricFlow AI** é uma aplicação Streamlit que integra duas APIs de IA (Mistral AI e OpenAI) para análise de iniciativas e geração de métricas, KPIs e OKRs. O projeto possui arquitetura clara de separação de responsabilidades, mas apresenta **pontos críticos** que precisam de atenção imediata:

| Categoria | Avaliação | Status |
|-----------|-----------|--------|
| Arquitetura | ⭐⭐⭐⭐ Bom | ✅ Aceitável |
| Segurança | ⭐⭐⭐ Regular | ⚠️ Requer atenção |
| Qualidade de Código | ⭐⭐⭐ Regular | ⚠️ Melhorias necessárias |
| Performance | ⭐⭐ Regular | ❌ Crítico |
| Testes | ⭐ Inexistente | ❌ Crítico |
| Documentação | ⭐⭐ Parcial | ⚠️ Incompleta |

**Principais achados:**
- ✅ Boa separação de serviços e validação de entrada
- ❌ Sem testes automatizados
- ❌ Sem uso de caching do Streamlit (performance crítica)
- ❌ Hardcoded API key fallback (`default_openai_key`, `default_mistral_key`)
- ❌ Falta `.env.example` para configuração
- ❌ Chamadas de IA síncronas bloqueiam a UI
- ⚠️ Template HTML simples, sem tratamento de XSS na renderização

---

## 2. INTRODUÇÃO

### 2.1 Objetivo do Projeto

O MetricFlow AI tem como objetivo gerar recomendações inteligentes de métricas, KPIs e OKRs a partir de descrições de iniciativas em linguagem natural. A aplicação combina:

- **Mistral AI** (`mistral-large-2512`) — Análise de contexto e classificação AARRR
- **OpenAI** (`gpt-4.1-mini`) — Geração de métricas, KPIs e OKRs
- **WeasyPrint** — Geração de relatórios PDF profissionais
- **Streamlit** — Interface web interativa

### 2.2 Tecnologias Principais

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | >= 3.11 | Runtime principal |
| Streamlit | >= 1.47.1 | Framework web |
| OpenAI SDK | >= 1.98.0 | Integração GPT |
| Requests | >= 2.32.4 | HTTP client (Mistral) |
| WeasyPrint | >= 66.0 | Geração de PDF |

---

## 3. ANÁLISE CRÍTICA DA ARQUITETURA

### 3.1 Visão Geral da Arquitetura Atual

```
┌─────────────────────────────────────────────────────────┐
│                     Streamlit UI (app.py)               │
│  ┌───────────┐  ┌───────────┐  ┌─────────────────────┐ │
│  │  Input    │→ │Validation │→ │   Progress Steps    │ │
│  │  User     │  │/Sanitize  │  │   (1-4)             │ │
│  └───────────┘  └───────────┘  └─────────────────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │
            ┌────────────┼────────────┐
            ↓            ↓            ↓
┌──────────────┐ ┌───────────┐ ┌──────────────────┐
│ MistralSvc   │ │ OpenAISvc │ │ PDFGenerator       │
│ (Classify)   │ │(Generate) │ │ (WeasyPrint)       │
└──────────────┘ └───────────┘ └──────────────────┘
```

**Fluxo de Dados:**
1. Entrada do usuário → Validação → Sanitização
2. Mistral AI analisa e classifica a iniciativa
3. OpenAI gera métricas baseadas no contexto
4. Dados compilados → PDF gerado → Download

### 3.2 Pontos Fortes

| # | Ponto Forte | Descrição |
|---|-------------|-----------|
| ✅ | Separação de Concerns | Serviços isolados em `services/`, utilitários em `utils/` |
| ✅ | Validação de Entrada | `validate_input()` e `sanitize_text()` bem implementados |
| ✅ | Tratamento de Erros | Try/except em serviços com fallback para Mistral |
| ✅ | UI Profissional | CSS customizado, progress steps, exemplos pré-definidos |
| ✅ | Templates | PDF template HTML separado da lógica |
| ✅ | Deploy Configurado | `render.yaml` e `requirements.txt` presentes |

### 3.3 Pontos Fracos e Oportunidades

| # | Problema | Impacto | Prioridade |
|---|----------|---------|------------|
| 🔴 | Sem caching no Streamlit | Re-executa chamadas de IA a cada rerender | **Crítico** |
| 🔴 | Fallback de API keys hardcoded | Risco de segurança e comportamento inesperado | **Alto** |
| 🔴 | Chamadas síncronas de IA | Bloqueio da UI por 30-60s | **Alto** |
| 🔴 | Sem testes automatizados | Nenhuma garantia de qualidade | **Crítico** |
| 🟡 | Sem `.env.example` | Dificulta setup inicial | **Médio** |
| 🟡 | Falha no parsing JSON | Pode quebrar com resposta mal formatada | **Médio** |
| 🟡 | Template sem sanitização HTML | Possível XSS via resposta de IA | **Médio** |
| 🟡 | Log de erros expõe stack trace | Informação técnica visível ao usuário | **Baixo** |

---

## 4. ANÁLISE DE QUALIDADE DE CÓDIGO

### 4.1 Conformidade com Padrões

**Aspectos Positivos:**
- ✅ Nomenclatura de classes e métodos segue PEP 8
- ✅ Uso de type hints (`Dict[str, Any]`, `List`)
- ✅ Docstrings presentes em métodos públicos

**Problemas Identificados:**

```python
# ❌ PROBLEMA 1: Mix de línguas em variáveis e comentários
etapa = context_analysis.get("etapa_funil", "N/A")  # Português
self.base_url = "https://api.mistral.ai/v1/chat/completions"  # Inglês

# ❌ PROBLEMA 2: CSS inline no app.py (~200 linhas de HTML/CSS misturado)
st.markdown("""
<div class="main-header">
    <h1>🧠 MetricFlow AI</h1>
</div>
""", unsafe_allow_html=True)

# ❌ PROBLEMA 3: Prompts de IA hardcoded inline (difícil manutenção)
prompt = f"""
Você é um especialista em métricas...
INICIATIVA: {initiative_text}
"""
```

**Recomendação:** Extrair prompts para arquivos de configuração (`config/prompts.yaml`).

### 4.2 Tratamento de Erros e Exceções

**Análise por Serviço:**

| Serviço | Cobertura | Problemas |
|---------|-----------|-----------|
| MistralService | ✅ Boa | Fallback JSON ok, mas retorna dados genéricos sem log |
| OpenAIService | ⚠️ Parcial | Não valida schema da resposta JSON |
| PDFGenerator | ⚠️ Parcial | Não verifica se template existe antes de abrir |
| app.py | ✅ Boa | Try/except com traceback exposto ao usuário |

**Problema Crítico — OpenAIService:**

```python
# ❌ Sem validação do schema JSON retornado
return json.loads(content)

# ✅ Recomendação:
data = json.loads(content)
required_fields = ["north_star_metric", "kpis", "okrs"]
for field in required_fields:
    if field not in data:
        raise ValueError(f"Campo obrigatório ausente: {field}")
return data
```

**Problema de Segurança — app.py:**

```python
# ❌ Stack trace exposto ao usuário final
with st.expander("🔍 **Detalhes Técnicos do Erro**"):
    st.error(f"Erro: {str(e)}")
    st.code(traceback.format_exc(), language="python")
```

### 4.3 Refatorações Sugeridas

**1. Extrair prompts para configuração:**

```yaml
# config/prompts.yaml
mistral:
  context_analysis: |
    Você é um especialista em análise de projetos e métricas de negócio.
    Analise a seguinte iniciativa e classifique-a nos critérios abaixo.
    INICIATIVA: {initiative_text}

openai:
  metrics_generation: |
    Você é um especialista em métricas de produto, KPIs e OKRs.
    INICIATIVA: {initiative_text}
    CONTEXTO: {context}
```

**2. Implementar retry com backoff:**

```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
        return wrapper
    return decorator
```

**3. Unificar serviços com interface comum:**

```python
from abc import ABC, abstractmethod

class AIService(ABC):
    @abstractmethod
    def analyze(self, text: str, context: dict = None) -> dict:
        pass

class MistralService(AIService):
    def analyze(self, text: str, context: dict = None) -> dict:
        return self.analyze_context(text)

class OpenAIService(AIService):
    def analyze(self, text: str, context: dict = None) -> dict:
        return self.generate_metrics(text, context)
```

---

## 5. ANÁLISE DE SEGURANÇA

### 5.1 Gerenciamento de Credenciais

**Problemas Identificados:**

| # | Problema | Arquivo | Linha | Severidade |
|---|----------|---------|-------|------------|
| 🔴 | Fallback de API key hardcoded | `openai_service.py` | 10 | **Alta** |
| 🔴 | Fallback de API key hardcoded | `mistral_service.py` | 10 | **Alta** |
| 🟡 | Sem `.env.example` | Raiz | — | **Média** |
| 🟡 | API keys não validadas | `app.py` | 194-199 | **Média** |

**Código Problemático:**

```python
# openai_service.py:10
self.api_key = os.getenv("OPENAI_API_KEY", "default_openai_key")
# ❌ Se variável não existir, usa chave hardcoded (inválida)

# mistral_service.py:10
self.api_key = os.getenv("MISTRAL_API_KEY", "default_mistral_key")
# ❌ Mesmo problema
```

**Recomendação:**

```python
def __init__(self):
    self.api_key = os.getenv("OPENAI_API_KEY")
    if not self.api_key:
        raise ValueError(
            "OPENAI_API_KEY não configurada. "
            "Defina a variável de ambiente antes de usar o serviço."
        )
    self.client = OpenAI(api_key=self.api_key)
```

**Arquivo `.env.example` recomendado:**

```bash
# .env.example
# Chaves de API para serviços de IA
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
MISTRAL_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Ambiente
STREAMLIT_ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 5.2 Vulnerabilidades Identificadas

| # | Vulnerabilidade | Tipo | Impacto | Mitigação |
|---|-----------------|------|---------|-----------|
| 🔴 | Template injection via IA | XSS | Alto | Sanitizar saída da IA antes de renderizar |
| 🟡 | Stack trace exposure | Info Leak | Médio | Remover traceback em produção |
| 🟡 | Prompt injection | Security | Médio | Validar e sanitar entrada do usuário |
| 🟢 | No rate limiting | DoS | Baixo | Implementar throttling |

**Exemplo de Template Injection:**

```python
# pdf_generator.py:57
replacements = {
    '{{INITIATIVE}}': data.get('initiative_description', ''),
    # ❌ Se a IA retornar HTML malicioso no JSON,
    # será injetado diretamente no template
}
```

---

## 6. ANÁLISE DE PERFORMANCE E OTIMIZAÇÃO

### 6.1 Desempenho da Aplicação

**Problema Crítico — Sem Caching:**

O Streamlit re-executa o script completo a cada interação. Sem `@st.cache_data` ou `@st.cache_resource`, as chamadas de IA são refeitas desnecessariamente.

```python
# ❌ Atual: Serviços instanciados a cada rerun
mistral_service = MistralService()
openai_service = OpenAIService()
pdf_generator = PDFGenerator()
```

**Recomendação — Cache de Recursos:**

```python
# ✅ Serviços devem ser cached (instanciação cara)
@st.cache_resource
def get_mistral_service():
    return MistralService()

@st.cache_resource
def get_openai_service():
    return OpenAIService()

@st.cache_resource
def get_pdf_generator():
    return PDFGenerator()
```

**Impacto Estimado:**

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| Instanciação | ~500ms | ~0ms (cache) | **99%** |
| Re-reruns | IA re-executada | Dados cached | **100%** |
| Memória | Nova cada vez | Compartilhada | **50%** |

### 6.2 Otimização de APIs de IA

**1. Timeouts configurados:**

```python
# Mistral: timeout=30 ✅ (ok)
# OpenAI: sem timeout ❌

response = self.client.chat.completions.create(
    model=self.model,
    messages=[...],
    # ❌ Adicionar timeout
    timeout=60.0
)
```

**2. Otimização de Prompts:**

| Problema | Impacto | Solução |
|----------|---------|---------|
| Prompts longos (~800 tokens) | Maior custo e latência | Reduzir para ~400 tokens |
| Sem system message eficiente | Respostas inconsistentes | Melhorar system prompt |
| JSON sem schema validation | Erros de parsing | Usar `response_format` com JSON Schema |

**3. Streaming para melhor UX:**

```python
# Em vez de esperar resposta completa, usar streaming
response = self.client.chat.completions.create(
    model=self.model,
    messages=[...],
    stream=True  # ✅ Mostra progresso em tempo real
)

for chunk in response:
    if chunk.choices[0].delta.content:
        yield chunk.choices[0].delta.content
```

---

## 7. RECOMENDAÇÕES DETALHADAS

### Prioridade Crítica 🔴

| # | Recomendação | Justificativa | Benefício |
|---|--------------|---------------|-----------|
| 1 | Adicionar `@st.cache_resource` nos serviços | Evita re-instanciação e re-execução de IA | Performance 10x melhor |
| 2 | Criar testes unitários básicos | Garante funcionamento correto | Qualidade e confiabilidade |
| 3 | Remover fallback de API keys hardcoded | Previne comportamento inesperado | Segurança e robustez |
| 4 | Adicionar `.env.example` | Facilita setup e onboarding | Developer Experience |

### Prioridade Alta 🟠

| # | Recomendação | Justificativa | Benefício |
|---|--------------|---------------|-----------|
| 5 | Implementar retry com backoff | APIs podem falhar temporariamente | Resiliência |
| 6 | Validar schema JSON da resposta | IA pode retornar formato inválido | Estabilidade |
| 7 | Sanitizar HTML no template PDF | Previne XSS | Segurança |
| 8 | Extrair prompts para configuração | Manutenibilidade | Clareza e flexibilidade |

### Prioridade Média 🟡

| # | Recomendação | Justificativa | Benefício |
|---|--------------|---------------|-----------|
| 9 | Adicionar logging estruturado | Debug em produção | Observabilidade |
| 10 | Remover traceback em produção | Info leak | Segurança |
| 11 | Implementar streaming de resposta | Melhor UX durante espera | Experiência do usuário |
| 12 | Adicionar integração contínua (CI) | Testes automáticos | Qualidade |

### Prioridade Baixa 🟢

| # | Recomendação | Justificativa | Benefício |
|---|--------------|---------------|-----------|
| 13 | Padronizar idioma (PT/EN) | Consistência | Manutenibilidade |
| 14 | Migrar Mistral para SDK oficial | Menos boilerplate | Simplicidade |
| 15 | Adicionar métricas de uso (analytics) | Entender uso do sistema | Data-driven decisions |

---

## 8. CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1 — Crítico (Imediato)

- [ ] **Adicionar caching de serviços**
  ```python
  @st.cache_resource
  def get_services():
      return MistralService(), OpenAIService(), PDFGenerator()
  ```

- [ ] **Remover fallback de API keys**
  - [ ] `openai_service.py`: Remover `"default_openai_key"`
  - [ ] `mistral_service.py`: Remover `"default_mistral_key"`
  - [ ] Lançar `ValueError` se chave não existir

- [ ] **Criar `.env.example`**
  - [ ] Incluir `OPENAI_API_KEY`, `MISTRAL_API_KEY`
  - [ ] Adicionar ao `.gitignore` (já está)

- [ ] **Criar testes unitários básicos**
  - [ ] `tests/test_validation.py` — Testar `validate_input` e `sanitize_text`
  - [ ] `tests/test_mistral_service.py` — Testar JSON parsing e fallback
  - [ ] `tests/test_openai_service.py` — Testar JSON parsing e limpeza de markdown

### Fase 2 — Alta Prioridade (1-2 semanas)

- [ ] **Implementar retry com backoff exponencial**
  - [ ] Decorador `@retry_with_backoff(max_retries=3)`
  - [ ] Aplicar em chamadas de API

- [ ] **Validar schema JSON das respostas**
  - [ ] Definir campos obrigatórios
  - [ ] Lançar erro descritivo se ausente

- [ ] **Sanitizar HTML no PDF template**
  - [ ] Usar `html.escape()` em dados antes de renderizar
  - [ ] Validar conteúdo antes de injetar

- [ ] **Extrair prompts para arquivos de configuração**
  - [ ] Criar `config/prompts.yaml`
  - [ ] Carregar prompts dinamicamente

### Fase 3 — Média Prioridade (2-4 semanas)

- [ ] **Adicionar logging estruturado**
  - [ ] Configurar `logging` module
  - [ ] Log de métricas: tempo de resposta, tokens usados

- [ ] **Remover traceback em produção**
  - [ ] Verificar `STREAMLIT_ENVIRONMENT`
  - [ ] Mostrar mensagem genérica ao usuário

- [ ] **Implementar streaming de resposta**
  - [ ] Usar `stream=True` na OpenAI
  - [ ] Mostrar progresso em tempo real no Streamlit

- [ ] **Configurar CI com GitHub Actions**
  - [ ] Pipeline de testes automáticos
  - [ ] Lint com ruff/flake8

### Fase 4 — Melhorias Contínuas

- [ ] Padronizar idioma do código (inglês para código, português para UI)
- [ ] Migrar Mistral para `mistralai` SDK oficial
- [ ] Adicionar analytics de uso (countly, plausible)
- [ ] Implementar rate limiting
- [ ] Adicionar suporte a múltiplos modelos de IA (configurável)

---

## 9. CONCLUSÃO

O **MetricFlow AI** é um projeto bem arquitetado com separação clara de responsabilidades e uma interface profissional. No entanto, a **ausência de caching** e **testes automatizados** são impedimentos críticos para produção.

As recomendações priorizadas neste relatório fornecem um roadmap claro para elevar a qualidade do projeto de ⭐⭐⭐ para ⭐⭐⭐⭐⭐, com foco em:

1. **Performance** → Caching + otimização de prompts
2. **Segurança** → Remover fallbacks + sanitização
3. **Confiabilidade** → Testes + retry + validação
4. **Manutenibilidade** → Configuração externa de prompts + logging

**Investimento estimado:** 2-4 semanas para implementação completa das recomendações críticas e altas.

---

> 📄 **Relatório gerado em 15/04/2026**  
> 🔄 **Próxima revisão:** Após implementação da Fase 1
