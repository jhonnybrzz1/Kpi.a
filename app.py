import streamlit as st
import os
from datetime import datetime
import traceback
import PyPDF2
import docx
from io import BytesIO

from services.mistral_service import MistralService
from services.openai_service import OpenAIService
from services.pdf_generator import PDFGenerator
from utils.validation import validate_input, sanitize_text

# Configuração da página
st.set_page_config(
    page_title="MetricFlow AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🧠 MetricFlow AI")
st.subheader("Sistema Inteligente de Sugestão de Métricas, KPIs e OKRs")

# Sidebar com informações
with st.sidebar:
    st.header("ℹ️ Como usar")
    st.markdown("""
    1. **Descreva sua iniciativa** no campo de texto
    2. **Clique em "Gerar Análise"** para processar
    3. **Aguarde o processamento** (30-60 segundos)
    4. **Baixe o relatório PDF** gerado
    """)
    
    st.header("📋 Exemplos de entrada")
    st.markdown("""
    - "Quero criar uma funcionalidade de notificação de estoque baixo no POS"
    - "Implementar sistema de fidelidade para clientes"
    - "Otimizar processo de onboarding de novos usuários"
    - "Desenvolver dashboard de vendas em tempo real"
    """)

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

def process_uploaded_file(uploaded_file):
    """Processa arquivo PRD carregado pelo usuário"""
    try:
        file_type = uploaded_file.type
        content = ""
        
        if file_type == "application/pdf":
            # Processa PDF
            pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
                
        elif file_type == "text/plain":
            # Processa arquivo TXT
            content = str(uploaded_file.read(), "utf-8")
            
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # Processa arquivo DOCX
            doc = docx.Document(BytesIO(uploaded_file.read()))
            content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
        elif uploaded_file.name.endswith('.md'):
            # Processa arquivo Markdown
            content = str(uploaded_file.read(), "utf-8")
            
        return content.strip()
        
    except Exception as e:
        st.warning(f"Erro ao processar arquivo: {str(e)}")
        return ""

# Interface principal
def main():
    if not check_api_keys():
        st.stop()
    
    # Campo de entrada
    st.header("📝 Descreva sua Iniciativa")
    user_input = st.text_area(
        "Digite uma descrição detalhada da sua iniciativa, projeto ou funcionalidade:",
        height=150,
        placeholder="Ex: Quero criar uma funcionalidade de notificação de estoque baixo no sistema POS para alertar gerentes quando produtos atingem quantidade mínima..."
    )
    
    # Upload de documento PRD (opcional)
    st.subheader("📎 Anexar Documento PRD (Opcional)")
    uploaded_file = st.file_uploader(
        "Faça upload de um documento PRD para análise mais detalhada:",
        type=['pdf', 'txt', 'docx', 'md'],
        help="Formatos aceitos: PDF, TXT, DOCX, Markdown"
    )
    
    # Campos opcionais
    responsible = st.text_input(
        "👤 Responsável (opcional)",
        placeholder="Nome do responsável pelo projeto"
    )
    
    # Botão de processamento
    if st.button("🚀 Gerar Análise MetricFlow", type="primary", use_container_width=True):
        
        # Validação da entrada
        validation_result = validate_input(user_input)
        if not validation_result["valid"]:
            st.error(f"❌ {validation_result['message']}")
            return
        
        # Sanitização do texto
        clean_input = sanitize_text(user_input)
        
        # Processamento
        with st.spinner("🔄 Processando sua solicitação..."):
            try:
                # Inicialização dos serviços
                mistral_service = MistralService()
                openai_service = OpenAIService()
                pdf_generator = PDFGenerator()
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Etapa 1: Análise com Mistral
                status_text.text("🧠 Analisando contexto com Mistral...")
                progress_bar.progress(25)
                
                context_analysis = mistral_service.analyze_context(clean_input)
                
                # Etapa 2: Geração de métricas com OpenAI
                status_text.text("📊 Gerando métricas e KPIs com GPT-4...")
                progress_bar.progress(50)
                
                # Processamento do arquivo PRD se fornecido
                prd_content = ""
                if uploaded_file is not None:
                    prd_content = process_uploaded_file(uploaded_file)
                
                # Combina descrição e PRD para análise de métricas
                full_context = clean_input
                if prd_content:
                    full_context += f"\n\nConteúdo do PRD anexado:\n{prd_content}"
                
                metrics_analysis = openai_service.generate_metrics(full_context, context_analysis)
                
                # Etapa 3: Compilação dos dados
                status_text.text("📝 Compilando relatório...")
                progress_bar.progress(75)
                
                # Preparação dos dados para o PDF
                report_data = {
                    "initiative_description": clean_input,
                    "prd_content": prd_content,
                    "responsible": responsible or "Não informado",
                    "date": datetime.now().strftime("%d/%m/%Y"),
                    "context_analysis": context_analysis,
                    "metrics_analysis": metrics_analysis
                }
                
                # Etapa 4: Geração do PDF
                status_text.text("📄 Gerando PDF...")
                progress_bar.progress(90)
                
                pdf_bytes = pdf_generator.generate_report(report_data)
                
                progress_bar.progress(100)
                status_text.text("✅ Análise concluída!")
                
                # Exibição dos resultados
                st.success("🎉 Relatório MetricFlow gerado com sucesso!")
                
                # Seção de resultados
                st.header("📊 Resultados da Análise")
                
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
                
                # Download do PDF
                st.header("📥 Download do Relatório")
                
                filename = f"Relatorio_MetricFlow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                st.download_button(
                    label="📄 Baixar Relatório PDF",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Erro durante o processamento: {str(e)}")
                with st.expander("🔍 Detalhes do erro (para desenvolvedores)"):
                    st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
