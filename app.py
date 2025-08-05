import streamlit as st
import os
from datetime import datetime
import traceback

from services.mistral_service import MistralService
from services.openai_service import OpenAIService
from services.pdf_generator import PDFGenerator
from utils.validation import validate_input, sanitize_text
from utils.examples import INITIATIVE_EXAMPLES

# Configuração da página
st.set_page_config(
    page_title="MetricFlow AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/metricflow-ai',
        'Report a bug': "https://github.com/your-repo/metricflow-ai/issues",
        'About': "MetricFlow AI - Sistema Inteligente de Métricas v1.0"
    }
)

# CSS personalizado para melhorar o layout
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.main-header h1 {
    margin: 0;
    font-size: 3rem;
    font-weight: bold;
}

.main-header p {
    margin: 0.5rem 0 0 0;
    font-size: 1.2rem;
    opacity: 0.9;
}

.feature-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    border-left: 4px solid #667eea;
    margin: 1rem 0;
}

.metric-badge {
    background: #f8f9fa;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    display: inline-block;
    margin: 0.2rem;
    border: 1px solid #dee2e6;
}

.stats-container {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
}

.workflow-step {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 3px solid #28a745;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.workflow-step h4 {
    margin: 0 0 0.5rem 0;
    color: #155724;
}

.ai-badge {
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: bold;
    display: inline-block;
    margin-left: 0.5rem;
}

.success-animation {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}
</style>
""", unsafe_allow_html=True)

# Cabeçalho principal melhorado
st.markdown("""
<div class="main-header">
    <h1>🧠 MetricFlow AI</h1>
    <p>Sistema Inteligente de Sugestão de Métricas, KPIs e OKRs</p>
    <p>✨ Powered by Mistral AI + OpenAI GPT-4 ✨</p>
</div>
""", unsafe_allow_html=True)

# Sidebar melhorada
with st.sidebar:
    st.markdown("### 🚀 **Como Funciona**")
    
    st.markdown("""
    <div class="workflow-step">
        <h4>1️⃣ Descreva sua Iniciativa</h4>
        <p>Digite detalhes do seu projeto ou funcionalidade</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="workflow-step">
        <h4>2️⃣ Análise Inteligente</h4>
        <p>IA analisa contexto e classifica o projeto</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="workflow-step">
        <h4>3️⃣ Geração de Métricas</h4>
        <p>Sistema cria KPIs e OKRs personalizados</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="workflow-step">
        <h4>4️⃣ Relatório PDF</h4>
        <p>Download do relatório completo</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 💡 **Exemplos de Iniciativas**")
    
    # Seletor de categoria
    categories = list(set([example["category"] for example in INITIATIVE_EXAMPLES.values()]))
    selected_category = st.selectbox(
        "🏷️ **Escolha uma Categoria:**",
        ["Todas as Categorias"] + categories,
        index=0
    )
    
    # Filtrar exemplos por categoria
    if selected_category == "Todas as Categorias":
        filtered_examples = INITIATIVE_EXAMPLES
    else:
        filtered_examples = {k: v for k, v in INITIATIVE_EXAMPLES.items() 
                           if v.get("category") == selected_category}
    
    # Botões de exemplo organizados
    for key, example in filtered_examples.items():
        if st.button(example["title"], use_container_width=True, key=f"btn_{key}"):
            st.session_state['example_text'] = example["description"]
            st.rerun()
    
    st.markdown("---")
    
    # Estatísticas do sistema
    st.markdown("""
    <div class="stats-container">
        <h4>📈 Estatísticas do Sistema</h4>
        <div class="metric-badge">🎯 +50 Tipos de KPIs</div>
        <div class="metric-badge">🔄 Análise AARRR</div>
        <div class="metric-badge">📋 Templates OKR</div>
        <div class="metric-badge">🤖 IA Dupla</div>
    </div>
    """, unsafe_allow_html=True)

# Verificação de API Keys
def check_api_keys():
    """Verifica se as API keys estão configuradas"""
    openai_key = os.getenv("OPENAI_API_KEY")
    mistral_key = os.getenv("MISTRAL_API_KEY")
    
    if not openai_key:
        st.error("❌ OPENAI_API_KEY não configurada nas variáveis de ambiente")
        return False
    
    if not mistral_key:
        st.error("❌ MISTRAL_API_KEY não configurada nas variáveis de ambiente")
        return False
    
    return True

# Interface principal
def main():
    if not check_api_keys():
        st.stop()
    
    # Seção de estatísticas rápidas
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric(
            label="🤖 Modelos IA",
            value="2",
            delta="Mistral + GPT-4"
        )
    
    with col_stat2:
        st.metric(
            label="📊 Tipos de Métricas",
            value="50+",
            delta="KPIs Personalizados"
        )
    
    with col_stat3:
        st.metric(
            label="⚡ Tempo Médio",
            value="45s",
            delta="Análise Completa"
        )
    
    with col_stat4:
        st.metric(
            label="📄 Formato Saída",
            value="PDF",
            delta="Profissional"
        )
    
    st.markdown("---")
    
    # Campo de entrada melhorado
    st.markdown("### 📝 **Descreva sua Iniciativa**")
    
    # Verifica se existe texto de exemplo na sessão
    default_text = st.session_state.get('example_text', '')
    
    user_input = st.text_area(
        "💡 **Digite uma descrição detalhada da sua iniciativa, projeto ou funcionalidade:**",
        height=180,
        placeholder="Ex: Quero criar uma funcionalidade de notificação de estoque baixo no sistema POS para alertar gerentes quando produtos atingem quantidade mínima...",
        value=default_text,
        help="Seja específico sobre objetivos, público-alvo e funcionalidades esperadas. Quanto mais detalhes, melhor será a análise!"
    )
    
    # Limpa o exemplo após usar
    if default_text:
        st.session_state['example_text'] = ''
    
    # Campos opcionais em layout melhorado
    st.markdown("### ⚙️ **Informações Adicionais** _(opcional)_")
    
    col1, col2 = st.columns(2)
    
    with col1:
        responsible = st.text_input(
            "👤 **Responsável pelo Projeto**",
            placeholder="Ex: João Silva - Product Manager",
            help="Nome e cargo da pessoa responsável pela iniciativa"
        )
    
    with col2:
        company = st.text_input(
            "🏢 **Empresa/Organização**",
            placeholder="Ex: TechCorp Ltda",
            help="Nome da empresa ou organização"
        )
    
    st.markdown("---")
    
    # Botão de processamento melhorado
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        generate_button = st.button(
            "🚀 **Gerar Análise MetricFlow**", 
            type="primary", 
            use_container_width=True,
            help="Clique para iniciar a análise inteligente da sua iniciativa"
        )
    
    if generate_button:
        
        # Validação da entrada
        validation_result = validate_input(user_input)
        if not validation_result["valid"]:
            st.error(f"❌ {validation_result['message']}")
            return
        
        # Sanitização do texto
        clean_input = sanitize_text(user_input)
        
        # Container de processamento melhorado
        processing_container = st.container()
        
        with processing_container:
            # Animação de carregamento personalizada
            st.markdown("""
            <div class="success-animation" style="text-align: center; padding: 2rem;">
                <h3>🔄 Processando sua Iniciativa...</h3>
                <p>Nossos modelos de IA estão analisando sua solicitação</p>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                # Inicialização dos serviços
                mistral_service = MistralService()
                openai_service = OpenAIService()
                pdf_generator = PDFGenerator()
                
                # Progress bar melhorada
                progress_container = st.container()
                
                with progress_container:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Etapa 1: Análise com Mistral
                    status_text.markdown("### 🧠 **Etapa 1/4:** Análise de Contexto com Mistral AI")
                    progress_bar.progress(25)
                    
                    context_analysis = mistral_service.analyze_context(clean_input)
                    
                    # Etapa 2: Geração de métricas com OpenAI
                    status_text.markdown("### 📊 **Etapa 2/4:** Geração de Métricas com GPT-4")
                    progress_bar.progress(50)
                    
                    metrics_analysis = openai_service.generate_metrics(clean_input, context_analysis)
                    
                    # Etapa 3: Compilação dos dados
                    status_text.markdown("### 📝 **Etapa 3/4:** Compilação do Relatório")
                    progress_bar.progress(75)
                    
                    # Preparação dos dados para o PDF
                    report_data = {
                        "initiative_description": clean_input,
                        "responsible": responsible or "Não informado",
                        "company": company or "Não informado",
                        "date": datetime.now().strftime("%d/%m/%Y"),
                        "context_analysis": context_analysis,
                        "metrics_analysis": metrics_analysis
                    }
                    
                    # Etapa 4: Geração do PDF
                    status_text.markdown("### 📄 **Etapa 4/4:** Gerando PDF Profissional")
                    progress_bar.progress(90)
                    
                    pdf_bytes = pdf_generator.generate_report(report_data)
                    
                    progress_bar.progress(100)
                    status_text.markdown("### ✅ **Análise Concluída com Sucesso!**")
                
                # Celebração de sucesso
                st.balloons()
                st.markdown("""
                <div class="success-animation" style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #d4edda, #c8e6c9); border-radius: 10px; margin: 1rem 0;">
                    <h2>🎉 Relatório MetricFlow Gerado com Sucesso!</h2>
                    <p>Sua análise inteligente está pronta para download</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Seção de resultados melhorada
                st.markdown("## 📊 **Resultados da Análise Inteligente**")
                
                # Contexto analisado pelo Mistral
                with st.expander("🧠 Análise de Contexto (Mistral)", expanded=True):
                    if context_analysis:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Tipo", context_analysis.get("tipo", "N/A"))
                        
                        with col2:
                            st.metric("Objetivo", context_analysis.get("objetivo", "N/A"))
                        
                        with col3:
                            st.metric("Etapa AARRR", context_analysis.get("etapa_funil", "N/A"))
                        
                        if context_analysis.get("justificativa"):
                            st.write("**Justificativa:**")
                            st.write(context_analysis["justificativa"])
                
                # Métricas geradas pelo OpenAI
                with st.expander("📈 Métricas e KPIs Sugeridos (GPT-4)", expanded=True):
                    if metrics_analysis:
                        if metrics_analysis.get("north_star_metric"):
                            st.write("**🌟 North Star Metric:**")
                            st.write(metrics_analysis["north_star_metric"])
                        
                        if metrics_analysis.get("kpis"):
                            st.write("**📊 KPIs Principais:**")
                            for i, kpi in enumerate(metrics_analysis["kpis"], 1):
                                st.write(f"{i}. **{kpi.get('nome', 'KPI')}:** {kpi.get('descricao', 'N/A')}")
                                if kpi.get("formula"):
                                    st.code(kpi["formula"])
                        
                        if metrics_analysis.get("okrs"):
                            st.write("**🎯 OKRs Sugeridos:**")
                            for okr in metrics_analysis["okrs"]:
                                st.write(f"**Objetivo:** {okr.get('objetivo', 'N/A')}")
                                if okr.get("key_results"):
                                    st.write("**Key Results:**")
                                    for kr in okr["key_results"]:
                                        st.write(f"- {kr}")
                
                # Download do PDF melhorado
                st.markdown("## 📥 **Download do Relatório**")
                
                filename = f"Relatorio_MetricFlow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                # Container centralizado para download
                col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
                
                with col_dl2:
                    st.download_button(
                        label="📄 **Baixar Relatório PDF Completo**",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary",
                        help="Clique para baixar seu relatório MetricFlow em PDF"
                    )
                    
                    # Informações sobre o arquivo
                    st.markdown(f"""
                    <div style="text-align: center; margin-top: 1rem; color: #666;">
                        <small>📁 Arquivo: {filename}</small><br>
                        <small>📊 Relatório completo com métricas, KPIs e OKRs</small>
                    </div>
                    """, unsafe_allow_html=True)
                
            except Exception as e:
                # Tratamento de erro melhorado
                st.markdown("""
                <div style="background: #f8d7da; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #dc3545; margin: 1rem 0;">
                    <h3 style="color: #721c24; margin-top: 0;">❌ Erro durante o Processamento</h3>
                    <p>Ocorreu um problema ao processar sua solicitação. Tente novamente em alguns instantes.</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("🔍 **Detalhes Técnicos do Erro**"):
                    st.error(f"Erro: {str(e)}")
                    st.code(traceback.format_exc(), language="python")
                    
                # Sugestões de solução
                st.markdown("""
                ### 💡 **Possíveis Soluções:**
                - ✅ Verifique se a descrição da iniciativa está completa
                - ✅ Certifique-se de que as APIs estão funcionando
                - ✅ Tente uma descrição mais detalhada
                - ✅ Aguarde alguns segundos e tente novamente
                """)

def add_footer():
    """Adiciona rodapé elegante à aplicação"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-radius: 10px; margin-top: 3rem;">
        <h4 style="color: #495057; margin-bottom: 1rem;">🧠 MetricFlow AI</h4>
        <p style="color: #6c757d; margin-bottom: 1rem;">
            Sistema Inteligente de Sugestão de Métricas, KPIs e OKRs<br>
            <small>Powered by Mistral AI + OpenAI GPT-4 | Versão 1.0</small>
        </p>
        <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
            <span style="background: #e3f2fd; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">🚀 IA Avançada</span>
            <span style="background: #f3e5f5; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">📊 Métricas SMART</span>
            <span style="background: #e8f5e8; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">📄 PDF Profissional</span>
            <span style="background: #fff3e0; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">⚡ Tempo Real</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    add_footer()
