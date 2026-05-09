# MetricFlow AI v2.0 🧠

## 🚀 Sistema Inteligente de Métricas, KPIs e OKRs

O **MetricFlow AI** é uma plataforma avançada construída com Streamlit que utiliza o poder combinado da **Mistral AI** e **OpenAI GPT-4o** para transformar descrições de iniciativas em métricas acionáveis, KPIs estratégicos e OKRs bem estruturados.

Esta versão 2.0 foca em **robustez técnica**, **segurança de dados** e **excelência na análise de contexto**.

---

## 🌟 Principais Recursos

- **Análise Multimodal de Contexto**: Utiliza `mistral-large-latest` para entender profundamente o domínio e os objetivos da iniciativa.
- **Motor de Métricas Especializado**: Aproveita o GPT-4o para gerar KPIs baseados em frameworks de mercado (AARRR, HEART, North Star).
- **Relatórios Executivos**: Geração automática de PDFs profissionais usando `xhtml2pdf`.
- **Segurança Enterprise**: Sanitização de inputs, proteção contra prompt injection e redação automática de dados sensíveis em logs.
- **Suporte a Documentos**: Extração de texto de arquivos PDF e DOCX para análise de contexto enriquecida.
- **Cache Inteligente**: Sistema de cache otimizado para reduzir latência e custos de API.

---

## 🛠️ Stack Tecnológica

- **Frontend/App**: [Streamlit](https://streamlit.io/)
- **Modelos de IA**: Mistral AI (Contexto) & OpenAI GPT-4o (Métricas)
- **Processamento de Documentos**: `pypdf`, `python-docx`
- **Geração de PDF**: `xhtml2pdf`, `markdown`
- **Validação de Dados**: `pydantic`, `PyYAML`
- **Infraestrutura**: Render.com (PaaS)

---

## 🏗️ Arquitetura do Sistema

O projeto segue uma estrutura modular para facilitar a manutenção e escalabilidade:

```text
├── app.py                 # Orquestrador principal da UI e fluxo de dados
├── services/              # Camada de integração com serviços externos
│   ├── mistral_service.py # Lógica de análise de contexto
│   ├── openai_service.py  # Lógica de geração de métricas
│   └── pdf_generator.py   # Motor de renderização de relatórios
├── ui/                    # Componentes modulares da interface
├── utils/                 # Utilitários de segurança, validação e telemetria
├── tests/                 # Suíte completa de testes unitários
└── config/                # Prompts estruturados em YAML
```

---

## 🔐 Segurança e Governança

O MetricFlow AI implementa diversas camadas de proteção:
- **Redação de Logs**: Filtros que impedem que chaves de API ou dados sensíveis do usuário cheguem aos logs.
- **Rate Limiting**: Limites por sessão para evitar abusos e controlar custos.
- **Validação de Input**: Sanitização rigorosa de todo texto inserido.
- **Proteção de Variáveis**: Gestão segura via `.env` e segredos do Streamlit.

---

## 🧪 Testes e Qualidade

O projeto conta com uma suíte de testes robusta baseada em `unittest`:
```bash
# Executar todos os testes
pytest tests/
```
Os testes cobrem validação de input, lógica de serviços, segurança e geração de chaves de cache.

---

## 🚀 Deploy e Execução Local

### Local
1. Clone e acesse o diretório: `git clone https://github.com/jhonnybrzz1/Kpi.a.git`
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure o `.env` (use `.env.example` como base).
4. Rode: `streamlit run app.py`

### Produção (Render)
O projeto está pré-configurado para o [Render](https://render.com/). Consulte `render.yaml` para detalhes da infraestrutura.

---

## 📊 Casos de Uso

- **Product Managers**: Definir métricas de sucesso para novas features.
- **Growth Hackers**: Estruturar funis AARRR baseados em IA.
- **Líderes de Engenharia**: Criar OKRs técnicos alinhados ao negócio.
- **Consultores**: Gerar relatórios de KPIs profissionais para stakeholders.

---

## 📄 Licença e Contribuição

Licenciado sob a **MIT License**. Sinta-se à vontade para abrir Issues ou Pull Requests seguindo as diretrizes de código limpo do projeto.

---
*MetricFlow AI — De dados brutos a decisões estratégicas.*