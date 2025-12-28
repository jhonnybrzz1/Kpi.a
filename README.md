# MetricFlow AI

## 🧠 Sistema Inteligente de Sugestão de Métricas, KPIs e OKRs

MetricFlow AI é uma aplicação Streamlit que utiliza inteligência artificial avançada para gerar métricas, KPIs e OKRs personalizados com base na descrição de projetos ou iniciativas. A aplicação combina os poderes da IA da Mistral AI e OpenAI GPT-4 para fornecer análises inteligentes e insights valiosos.

## 🌟 Recursos

- **Análise de Contexto Inteligente**: Utiliza Mistral AI para entender o contexto do seu projeto
- **Geração de Métricas Avançadas**: Emprega GPT-4 para sugerir KPIs e OKRs relevantes
- **Relatórios Profissionais em PDF**: Gera relatórios completos e formatados
- **Interface Intuitiva**: Design moderno e amigável com Streamlit
- **Sistema de Classificação AARRR**: Análise baseada no modelo de crescimento AARRR (Acquisition, Activation, Retention, Revenue, Referral)
- **Exemplos de Iniciativas**: Biblioteca de exemplos para inspirar e guiar

## 🛠️ Tecnologias Utilizadas

- Python
- Streamlit
- Mistral AI API
- OpenAI GPT-4 API
- PDF Generator
- Streamlit Components

## 🚀 Instalação e Execução

1. Clone este repositório:
```bash
git clone https://github.com/jhonnybrzz1/Kpi.a.git
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
# ou se estiver usando uv
uv pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
# Crie um arquivo .env com suas chaves de API
OPENAI_API_KEY=sua_chave_openai
MISTRAL_API_KEY=sua_chave_mistral
```

4. Execute a aplicação:
```bash
streamlit run app.py
```

## 🔐 Configuração de API Keys

A aplicação requer chaves de API válidas para ambos os serviços de IA:

- **OPENAI_API_KEY**: Sua chave de API do OpenAI (usando o modelo GPT-4o)
- **MISTRAL_API_KEY**: Sua chave de API da Mistral AI (usando o modelo mistral-large-2512)

## 📊 Funcionalidades

1. **Descrição da Iniciativa**: Insira uma descrição detalhada do seu projeto ou funcionalidade
2. **Análise de Contexto**: A IA analisa e classifica sua iniciativa
3. **Geração de Métricas**: Criação de KPIs e OKRs personalizados
4. **Relatório PDF**: Download de um relatório profissional com todas as métricas
5. **Sistema de Exemplos**: Acesso a exemplos de iniciativas para referência

## 📁 Estrutura do Projeto

```
├── app.py                 # Aplicação Streamlit principal
├── services/              # Serviços de IA
│   ├── mistral_service.py # Integração com Mistral AI
│   ├── openai_service.py  # Integração com OpenAI
│   └── pdf_generator.py   # Geração de relatórios PDF
├── utils/                 # Utilitários
│   ├── validation.py      # Validação de entrada
│   └── examples.py        # Exemplos de iniciativas
├── .env.example          # Exemplo de variáveis de ambiente
└── requirements.txt      # Dependências do projeto
```

## 🎯 Casos de Uso

- Definição de métricas para novos produtos ou funcionalidades
- Estabelecimento de OKRs para equipes e projetos
- Análise de métricas baseadas no modelo AARRR
- Geração de relatórios de métricas para stakeholders
- Planejamento estratégico baseado em dados

## 🤝 Contribuição

Sinta-se à vontade para contribuir com este projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob os termos descritos no arquivo LICENSE.

## 📞 Suporte

Para suporte, abra uma issue no repositório ou entre em contato através das informações disponíveis no menu "About" da aplicação.