# MetricFlow AI 🧠

### Sistema Inteligente de Sugestão de Métricas, KPIs e OKRs

O **MetricFlow AI** é uma plataforma analítica desenvolvida em Streamlit que orquestra modelos de linguagem de larga escala (LLMs) para converter descrições de iniciativas de negócio em frameworks de medição estruturados. O sistema utiliza a **Mistral AI** para análise profunda de contexto e o **OpenRouter Gemma 4** para a geração técnica de KPIs e OKRs.

---

## 🛠 Stack Tecnológica

- **Linguagem**: Python 3.11+
- **Interface**: [Streamlit](https://streamlit.io/)
- **Modelos de IA**:
    - **Mistral AI**: `mistral-large-latest` (Análise de Contexto)
    - **OpenRouter**: `google/gemma-4-31b-it` (Geração de Métricas e Resumo Executivo)
- **Extração de Documentos**: `pypdf`, `python-docx`
- **Geração de Relatórios**: `xhtml2pdf`, `markdown`
- **Segurança e Validação**: `pydantic`, `PyYAML`
- **Qualidade de Código**: `pytest`, `ruff`

---

## 🏗 Arquitetura do Projeto

O repositório segue uma estrutura modular e desacoplada:

```text
├── app.py                 # Orquestrador principal e interface Streamlit
├── config/                # Gerenciamento de prompts estruturados (YAML)
├── services/              # Camada de integração com APIs externas e lógica core
│   ├── mistral_service.py # Engine de análise contextual
│   ├── openai_service.py  # Engine OpenRouter de geração de métricas/resumos
│   └── pdf_generator.py   # Renderização de relatórios técnicos
├── ui/                    # Componentes modulares da interface de usuário
├── utils/                 # Utilitários de segurança, telemetria, cache e validação
├── data/                  # Benchmarks e datasets de referência
└── tests/                 # Suíte de testes automatizados
```

---

## 🚀 Como Iniciar

### Pré-requisitos
- Python 3.11 ou superior
- Git
- Chaves de API: Mistral AI e OpenRouter

### Instalação Local

1. **Clonar o Repositório**:
   ```bash
   git clone https://github.com/jhonnybrzz1/Kpi.a.git
   cd Kpi.a
   ```

2. **Criar Ambiente Virtual**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # ou
   .venv\Scripts\activate     # Windows
   ```

3. **Instalar Dependências**:
   ```bash
   pip install -r requirements.txt
   ```

### Configuração
Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:
```env
OPENROUTER_API_KEY=sua_chave_aqui
OPENROUTER_MODEL=google/gemma-4-31b-it
OPENROUTER_API_URL=https://openrouter.ai/api/v1
MISTRAL_API_KEY=sua_chave_aqui
STREAMLIT_ENVIRONMENT=development
```

---

## 💻 Execução

Inicie a aplicação localmente com o comando:
```bash
streamlit run app.py
```

Acesse via navegador no endereço padrão: `http://localhost:8501`.

---

## 🧪 Desenvolvimento e Testes

### Executar Testes
O projeto utiliza `pytest` para garantir a integridade dos serviços e utilitários:
```bash
pytest tests/
```

### Linting e Formatação
Mantemos a qualidade do código com `ruff`:
```bash
ruff check .
```

---

## 🔐 Segurança

O MetricFlow AI implementa:
- **Sanitização de Inputs**: Proteção contra ataques de Prompt Injection.
- **Redação de Logs**: Filtros automáticos que impedem o vazamento de chaves e dados sensíveis.
- **Rate Limiting**: Controle de chamadas por sessão para gestão de custos de API.

---

## 📄 Licença
Este projeto está licenciado sob a **MIT License**.

---
*MetricFlow AI — Transformando visão em métricas acionáveis.*
