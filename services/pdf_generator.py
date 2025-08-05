import os
from datetime import datetime
from typing import Dict, Any
import json
from weasyprint import HTML, CSS
from io import BytesIO

class PDFGenerator:
    """Gerador de relatórios PDF usando WeasyPrint"""
    
    def __init__(self):
        self.template_path = "templates/pdf_template.html"
    
    def generate_report(self, data: Dict[str, Any]) -> bytes:
        """
        Gera relatório PDF completo
        
        Args:
            data: Dados do relatório
            
        Returns:
            bytes: PDF gerado
        """
        
        try:
            # Carrega o template HTML
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Substitui as variáveis no template
            html_content = self._render_template(template, data)
            
            # Gera o PDF
            html_doc = HTML(string=html_content)
            pdf_bytes = html_doc.write_pdf()
            
            if pdf_bytes is None:
                raise Exception("Falha na geração do PDF")
            
            return pdf_bytes
            
        except Exception as e:
            raise Exception(f"Erro ao gerar PDF: {str(e)}")
    
    def _render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Renderiza o template com os dados fornecidos"""
        
        # Preparação dos dados
        context = data.get('context_analysis', {})
        metrics = data.get('metrics_analysis', {})
        
        # Formatação das seções
        kpis_html = self._format_kpis(metrics.get('kpis', []))
        okrs_html = self._format_okrs(metrics.get('okrs', []))
        frameworks_html = self._format_frameworks(metrics.get('frameworks_aplicaveis', []))
        implementation_html = self._format_implementation(metrics.get('implementacao_medicao', {}))
        
        # Substituições no template
        replacements = {
            '{{RESPONSIBLE}}': data.get('responsible', 'Não informado'),
            '{{DATE}}': data.get('date', datetime.now().strftime('%d/%m/%Y')),
            '{{INITIATIVE}}': data.get('initiative_description', ''),
            '{{CONTEXT_TYPE}}': context.get('tipo', 'N/A'),
            '{{CONTEXT_OBJECTIVE}}': context.get('objetivo', 'N/A'),
            '{{CONTEXT_FUNNEL}}': context.get('etapa_funil', 'N/A'),
            '{{CONTEXT_COMPLEXITY}}': context.get('complexidade', 'N/A'),
            '{{CONTEXT_AREAS}}': ', '.join(context.get('area_impacto', [])),
            '{{CONTEXT_JUSTIFICATION}}': context.get('justificativa', ''),
            '{{NORTH_STAR_NAME}}': metrics.get('north_star_metric', {}).get('nome', 'N/A'),
            '{{NORTH_STAR_DESC}}': metrics.get('north_star_metric', {}).get('descricao', ''),
            '{{NORTH_STAR_JUST}}': metrics.get('north_star_metric', {}).get('justificativa', ''),
            '{{KPIS_LIST}}': kpis_html,
            '{{OKRS_LIST}}': okrs_html,
            '{{FRAMEWORKS_LIST}}': frameworks_html,
            '{{IMPLEMENTATION_DETAILS}}': implementation_html,
            '{{RISKS_LIST}}': self._format_risks(metrics.get('riscos_metricas', [])),
            '{{NEXT_STEPS_LIST}}': self._format_next_steps(metrics.get('proximos_passos', []))
        }
        
        # Aplica as substituições
        rendered_html = template
        for placeholder, value in replacements.items():
            rendered_html = rendered_html.replace(placeholder, str(value))
        
        return rendered_html
    
    def _format_kpis(self, kpis: list) -> str:
        """Formata lista de KPIs para HTML"""
        if not kpis:
            return "<p>Nenhum KPI específico foi gerado.</p>"
        
        html = ""
        for i, kpi in enumerate(kpis, 1):
            html += f"""
            <div class="kpi-item">
                <h4>{i}. {kpi.get('nome', 'KPI sem nome')}</h4>
                <p><strong>Descrição:</strong> {kpi.get('descricao', 'Sem descrição')}</p>
                <p><strong>Fórmula:</strong> <code>{kpi.get('formula', 'Não especificada')}</code></p>
                <p><strong>Frequência:</strong> {kpi.get('frequencia_medicao', 'Não especificada')}</p>
                <p><strong>Meta sugerida:</strong> {kpi.get('meta_sugerida', 'Não especificada')}</p>
                <p><strong>Área responsável:</strong> {kpi.get('responsavel_area', 'Não especificada')}</p>
            </div>
            """
        
        return html
    
    def _format_okrs(self, okrs: list) -> str:
        """Formata lista de OKRs para HTML"""
        if not okrs:
            return "<p>Nenhum OKR específico foi gerado.</p>"
        
        html = ""
        for i, okr in enumerate(okrs, 1):
            key_results = okr.get('key_results', [])
            kr_html = ""
            for kr in key_results:
                kr_html += f"<li>{kr}</li>"
            
            html += f"""
            <div class="okr-item">
                <h4>OKR {i}: {okr.get('objetivo', 'Objetivo não especificado')}</h4>
                <p><strong>Prazo:</strong> {okr.get('prazo', 'Não especificado')}</p>
                <p><strong>Key Results:</strong></p>
                <ul>{kr_html}</ul>
            </div>
            """
        
        return html
    
    def _format_frameworks(self, frameworks: list) -> str:
        """Formata lista de frameworks para HTML"""
        if not frameworks:
            return "<p>Nenhum framework específico foi identificado.</p>"
        
        html = ""
        for framework in frameworks:
            html += f"""
            <div class="framework-item">
                <h4>{framework.get('nome', 'Framework')}</h4>
                <p>{framework.get('aplicacao', 'Aplicação não especificada')}</p>
            </div>
            """
        
        return html
    
    def _format_implementation(self, implementation: dict) -> str:
        """Formata detalhes de implementação para HTML"""
        if not implementation:
            return "<p>Detalhes de implementação não especificados.</p>"
        
        tools = implementation.get('ferramentas_sugeridas', [])
        tools_html = ""
        for tool in tools:
            tools_html += f"<li>{tool}</li>"
        
        html = f"""
        <div class="implementation-details">
            <h4>Ferramentas Sugeridas:</h4>
            <ul>{tools_html}</ul>
            
            <h4>Setup de Tracking:</h4>
            <p>{implementation.get('setup_tracking', 'Não especificado')}</p>
            
            <h4>Dashboards:</h4>
            <p>{implementation.get('dashboards', 'Não especificado')}</p>
        </div>
        """
        
        return html
    
    def _format_risks(self, risks: list) -> str:
        """Formata lista de riscos para HTML"""
        if not risks:
            return "<p>Nenhum risco específico foi identificado.</p>"
        
        html = "<ul>"
        for risk in risks:
            html += f"<li>{risk}</li>"
        html += "</ul>"
        
        return html
    
    def _format_next_steps(self, steps: list) -> str:
        """Formata lista de próximos passos para HTML"""
        if not steps:
            return "<p>Nenhum próximo passo específico foi gerado.</p>"
        
        html = "<ul>"
        for step in steps:
            html += f"<li>{step}</li>"
        html += "</ul>"
        
        return html
