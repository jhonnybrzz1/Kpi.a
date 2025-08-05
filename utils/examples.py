"""
Exemplos pré-definidos de iniciativas para facilitar testes do sistema
"""

INITIATIVE_EXAMPLES = {
    "app_fidelidade": {
        "title": "📱 App de Fidelidade",
        "description": "Desenvolver um aplicativo mobile de programa de fidelidade que permita aos clientes acumular pontos a cada compra, resgatar recompensas exclusivas, receber ofertas personalizadas baseadas no histórico de compras e acompanhar status VIP com benefícios especiais.",
        "category": "Mobile & Engagement"
    },
    
    "dashboard_analytics": {
        "title": "📊 Dashboard Analytics",
        "description": "Criar um dashboard executivo em tempo real que consolide métricas de vendas, performance de produtos, satisfação do cliente e KPIs operacionais, com filtros por período, região e categoria, incluindo alertas automáticos para anomalias.",
        "category": "Analytics & BI"
    },
    
    "sistema_notificacoes": {
        "title": "🔔 Sistema de Notificações",
        "description": "Implementar sistema inteligente de notificações push e email que envie alertas personalizados sobre promoções, status de pedidos, recomendações de produtos e lembretes de carrinho abandonado, segmentado por perfil de cliente.",
        "category": "Marketing & Communication"
    },
    
    "automacao_processos": {
        "title": "⚙️ Automação de Processos",
        "description": "Automatizar processo de onboarding de novos funcionários incluindo criação de contas, treinamentos obrigatórios, assinatura digital de documentos, configuração de acessos e acompanhamento de progresso até conclusão.",
        "category": "HR & Operations"
    },
    
    "chatbot_atendimento": {
        "title": "🤖 Chatbot Inteligente",
        "description": "Desenvolver chatbot com IA para atendimento ao cliente 24/7, capaz de resolver dúvidas frequentes, processar solicitações simples, agendar callbacks e escalar casos complexos para atendentes humanos, integrado com WhatsApp e site.",
        "category": "Customer Service"
    },
    
    "marketplace_interno": {
        "title": "🏪 Marketplace Interno",
        "description": "Criar plataforma interna tipo marketplace onde diferentes departamentos podem solicitar serviços de outros setores, com sistema de aprovação, tracking de projetos, avaliações de qualidade e métricas de performance inter-departamental.",
        "category": "Internal Operations"
    },
    
    "sistema_gamificacao": {
        "title": "🎮 Sistema de Gamificação",
        "description": "Implementar sistema de gamificação para equipe de vendas com rankings, badges, desafios mensais, recompensas por metas atingidas e torneios entre filiais, incluindo dashboard de performance e premiações automáticas.",
        "category": "Sales & Motivation"
    },
    
    "plataforma_feedback": {
        "title": "💬 Plataforma de Feedback",
        "description": "Construir plataforma para coleta e gestão de feedback de clientes pós-compra, com questionários personalizados, análise de sentimento automatizada, dashboard de NPS e ações automáticas baseadas nas respostas coletadas.",
        "category": "Customer Experience"
    }
}

def get_example_by_key(key: str) -> dict:
    """Retorna exemplo específico por chave"""
    return INITIATIVE_EXAMPLES.get(key, {})

def get_all_examples() -> dict:
    """Retorna todos os exemplos disponíveis"""
    return INITIATIVE_EXAMPLES

def get_examples_by_category(category: str) -> dict:
    """Retorna exemplos de uma categoria específica"""
    return {k: v for k, v in INITIATIVE_EXAMPLES.items() if v.get("category") == category}