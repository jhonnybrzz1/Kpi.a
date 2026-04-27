import html
import markdown
import json
from datetime import datetime
from typing import Any, Dict, List
from weasyprint import HTML

class PDFGenerator:
    def __init__(self):
        self.template_path = "templates/pdf_template.html"

    def generate_report(self, data: Dict[str, Any]) -> bytes:
        try:
            with open(self.template_path, "r", encoding="utf-8") as f:
                template = f.read()
            html_content = self._render_template(template, data)
            pdf_bytes = HTML(string=html_content).write_pdf()
            if pdf_bytes is None:
                raise Exception("Falha na geração dos bytes do PDF")
            return pdf_bytes
        except Exception as e:
            raise Exception(f"Erro ao gerar PDF: {str(e)}")

    def _md(self, text: str) -> str:
        if not text: return ""
        if isinstance(text, (dict, list)):
            text = json.dumps(text, ensure_ascii=False)
        return markdown.markdown(str(text))

    def _e(self, value: Any) -> str:
        if value is None: return ""
        return html.escape(str(value))

    def _format_data_identified(self, data: Any) -> str:
        """Formata os dados identificados em uma lista HTML elegante."""
        if not data: return "Nenhum dado mencionado"
        
        # Tenta converter string JSON em dicionário se necessário
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except:
                return self._e(data)
        
        if isinstance(data, dict):
            html_out = '<ul style="list-style:none; padding:0; margin:0;">'
            for key, value in data.items():
                label = key.replace("_", " ").title()
                if isinstance(value, list):
                    value = ", ".join([str(v) for v in value])
                html_out += f'<li style="margin-bottom:5px;"><strong>{self._e(label)}:</strong> {self._e(value)}</li>'
            html_out += '</ul>'
            return html_out
        
        return self._e(data)

    def _render_template(self, template: str, data: Dict[str, Any]) -> str:
        ctx = data.get("context_analysis", {})
        m = data.get("metrics_analysis", {})
        ns = m.get("north_star", {})

        replacements = {
            "{{DATE}}": data.get("date", datetime.now().strftime("%d/%m/%Y")),
            "{{RESPONSIBLE}}": self._e(data.get("responsible", "N/A")),
            "{{COMPANY}}": self._e(data.get("company", "N/A")),
            "{{CONTEXT_TYPE}}": self._e(ctx.get("tipo", "N/A")),
            "{{CONTEXT_GAME}}": self._e(ctx.get("business_game", "N/A")),
            "{{CONTEXT_OBJECTIVE}}": self._e(ctx.get("objetivo", "N/A")),
            "{{CONTEXT_FUNNEL}}": self._e(ctx.get("etapa_funil", "N/A")),
            "{{CONTEXT_PRD}}": self._e(ctx.get("resumo_prd", ctx.get("valor_entregue", "N/A"))),
            "{{CONTEXT_DATA}}": self._format_data_identified(ctx.get("dados_atuais")),
            "{{CONTEXT_JUSTIFICATION}}": self._md(ctx.get("justificativa", "")),
            "{{NSM_NAME}}": self._e(ns.get("nome", "N/A")),
            "{{NSM_DESC}}": self._e(ns.get("justificativa", "")),
            "{{NSM_FORMULA}}": self._e(ns.get("definicao", "N/A")),
            "{{NSM_SMART}}": self._e(", ".join(ns.get("validacao_smart", []))),
            "{{L1_METRICS}}": self._render_l1(m.get("l1_health_indicators", [])),
            "{{L2_METRICS}}": self._render_l2(m.get("l2_diagnostic_metrics", [])),
            "{{OKRS}}": self._render_okrs(m.get("okrs", [])),
            "{{COUNTER_METRICS}}": self._render_counter(m.get("counter_metrics", [])),
            "{{TOOLS}}": self._e(", ".join(m.get("implementacao", {}).get("ferramentas", []))),
            "{{VISUALIZATION}}": self._e(m.get("implementacao", {}).get("visualizacao", "N/A")),
            "{{RISKS}}": self._e(", ".join(m.get("riscos_e_vieses", []))),
        }

        rendered = template
        for k, v in replacements.items():
            rendered = rendered.replace(k, str(v))
        return rendered

    def _render_l1(self, items: List[Dict]) -> str:
        if not items: return "<p>Não disponível</p>"
        html_out = "<table><thead><tr><th>Pilar</th><th>Métrica</th><th>Meta Sugerida</th></tr></thead><tbody>"
        for item in items:
            html_out += f"""
            <tr>
                <td><span class="badge">{self._e(item.get('pilar'))}</span></td>
                <td><strong>{self._e(item.get('metrica'))}</strong><br><small>{self._e(item.get('por_que_importa'))}</small></td>
                <td>{self._e(item.get('meta_sugerida'))}</td>
            </tr>"""
        html_out += "</tbody></table>"
        return html_out

    def _render_l2(self, items: List[Dict]) -> str:
        if not items: return "<p>Não disponível</p>"
        html_out = ""
        for item in items:
            html_out += f"""
            <div class="card">
                <small style="color:#6366f1">Vínculo: {self._e(item.get('vinculo_l1'))}</small><br>
                <strong>{self._e(item.get('metrica'))}</strong>
                <div class="warning-text">⚠️ Ação se cair: {self._e(item.get('acao_se_cair'))}</div>
            </div>"""
        return html_out

    def _render_okrs(self, items: List[Dict]) -> str:
        if not items: return "<p>Não disponível</p>"
        html_out = ""
        for okr in items:
            krs = ""
            for kr in okr.get("key_results", []):
                krs += f"""
                <div class="okr-card">
                    <strong>{self._e(kr.get('resultado'))}</strong><br>
                    <span class="kr-meta">Baseline: {self._e(kr.get('baseline'))} | Meta: {self._e(kr.get('meta'))}</span>
                </div>"""
            html_out += f"""
            <div class="card">
                <h4 style="margin:0 0 10px 0;">🎯 {self._e(okr.get('objetivo'))}</h4>
                {krs}
            </div>"""
        return html_out

    def _render_counter(self, items: List[Dict]) -> str:
        if not items: return "<p>Não disponível</p>"
        html_out = ""
        for item in items:
            html_out += f"""
            <div class="card" style="border-left: 4px solid #ef4444">
                <strong>🛡️ {self._e(item.get('nome'))}</strong><br>
                <small>Protege contra: {self._e(item.get('protege_contra'))}</small><br>
                <small style="color:#b91c1c">Trade-off: {self._e(item.get('trade_off'))}</small>
            </div>"""
        return html_out
