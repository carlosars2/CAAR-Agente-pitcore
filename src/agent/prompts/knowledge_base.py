"""
Pitcore Agent - Knowledge Base
Structured product data for the Pitcore & Systems AI agent.
"""

AGENTS = [
    {
        "id": "atendimento",
        "name": "Agente de Atendimento",
        "description": "Transforme mensagens em agendamentos — automaticamente. Atende, qualifica e organiza toda a comunicacao via WhatsApp 24/7.",
        "features": [
            "Qualificacao automatica por tipo de servico",
            "Respostas inteligentes baseadas em padroes de atendimento",
            "Encaminhamento direto ao responsavel",
            "Historico centralizado de conversas",
        ],
        "result": "Menos mensagens perdidas, mais carros no box.",
        "use_case": "Centro automotivo que perde clientes porque demora para responder WhatsApp ou nao consegue organizar a fila de atendimento.",
    },
    {
        "id": "orcamento",
        "name": "Agente de Orcamento",
        "description": "Reduza o tempo de orcamento e aumente a taxa de aprovacao. Gera orcamentos automaticamente a partir de texto ou audio.",
        "features": [
            "Interpretacao inteligente de sintomas e solicitacoes",
            "Sugestao automatica de servicos aplicaveis",
            "Padronizacao de precos e descricoes",
            "Envio imediato com solicitacao de aprovacao",
        ],
        "result": "Mais agilidade, menos erros e maior conversao.",
        "use_case": "Oficina que demora horas para montar orcamento, ou que perde aprovacao porque o cliente esfria enquanto espera.",
    },
    {
        "id": "cobranca",
        "name": "Agente de Cobranca",
        "description": "Reduza inadimplencia sem desgastar relacionamento. Automatiza lembretes e follow-ups de pagamento de forma estrategica.",
        "features": [
            "Lembretes automaticos no momento certo",
            "Regras inteligentes de cobranca por perfil",
            "Notificacoes via WhatsApp e email",
            "Monitoramento de inadimplencia em tempo real",
        ],
        "result": "Melhora do fluxo de caixa e menos tempo cobrando clientes.",
        "use_case": "Centro que tem dinheiro a receber mas nao cobra de forma sistematica, ou que perde a relacao com o cliente por cobrar de forma inadequada.",
    },
    {
        "id": "gestao",
        "name": "Agente de Gestao",
        "description": "Tenha clareza diaria do que esta funcionando e do que esta travando. Analisa dados operacionais e financeiros.",
        "features": [
            "KPIs essenciais consolidados",
            "Alertas de gargalos operacionais",
            "Resumo diario via WhatsApp",
            "Identificacao de padroes e anomalias",
        ],
        "result": "Decisoes mais rapidas e menos prejuizos invisiveis.",
        "use_case": "Dono de oficina que nao tem visibilidade clara dos numeros e toma decisoes no feeling.",
    },
    {
        "id": "estoque",
        "name": "Agente de Estoque",
        "description": "Pare de perder dinheiro com falta ou excesso de pecas. Monitora giro, demanda e historico de servicos.",
        "features": [
            "Previsao inteligente de reposicao",
            "Curva ABC automatica",
            "Alertas de estoque critico",
            "Sugestao de compras baseada em historico",
        ],
        "result": "Menos emergencia, menos desperdicio e melhor margem.",
        "use_case": "Oficina que para servico por falta de peca, ou que tem capital empatado em estoque parado.",
    },
    {
        "id": "margem",
        "name": "Agente de Margem",
        "description": "Descubra onde voce realmente ganha e onde esta perdendo. Analisa rentabilidade por OS, tecnico e tipo de trabalho.",
        "features": [
            "Margem real por ordem de servico",
            "Comparativo por tecnico e tipo de servico",
            "Alertas de baixa rentabilidade",
            "Acompanhamento de evolucao da margem",
        ],
        "result": "Ajuste estrategico de precos e aumento consistente de lucro.",
        "use_case": "Centro que fatura bem mas nao sabe exatamente onde ganha e onde perde dinheiro em cada servico.",
    },
    {
        "id": "garantia",
        "name": "Agente de Garantia",
        "description": "Reduza retrabalho e proteja sua reputacao. Monitora ocorrencias de garantia e identifica padroes de retrabalho.",
        "features": [
            "Rastreamento automatico de retornos",
            "Indice de qualidade por tecnico",
            "Alertas de vencimento de garantia",
            "Relatorios de recorrencia",
        ],
        "result": "Menos custo oculto e mais controle de qualidade.",
        "use_case": "Oficina que tem retrabalho frequente e nao consegue identificar se o problema e peca, tecnico ou processo.",
    },
]

# Nao existem pacotes pre-definidos. Cada solucao e montada sob medida
# com os agentes mais adequados para o caso do cliente.
# A combinacao e definida na consulta com especialista.

BUILD_SOB_MEDIDA = {
    "name": "Build Sob Medida",
    "description": "Sistema 100% customizado para seu centro automotivo. Projetado do zero para o fluxo real do seu negocio. Valores definidos na consulta com especialista.",
    "project_types": [
        {"id": "crm", "name": "CRM & Vendas", "description": "Funil de vendas, precificacao inteligente, planos recorrentes, historico do cliente."},
        {"id": "operacao", "name": "Operacao", "description": "Ordens de servico inteligentes, checklists, aprovacao digital, timeline do veiculo."},
        {"id": "estoque", "name": "Estoque & Pecas", "description": "Estoque multi-local, reposicao automatica, curva ABC, sugestoes de compra."},
        {"id": "financeiro", "name": "Financeiro & Faturamento", "description": "Contas a pagar/receber, comissoes automaticas, DRE gerencial, centros de custo."},
        {"id": "rh", "name": "Produtividade & RH", "description": "Produtividade de tecnicos, metas e performance, escalas, execucao com qualidade."},
        {"id": "cliente", "name": "Experiencia do Cliente", "description": "Agendamento inteligente, portal do cliente, comunicacao automatizada, pos-venda."},
        {"id": "bi", "name": "BI & Dados", "description": "Dashboards estrategicos, indicadores operacionais, analise de clientes, comparativos multi-unidade."},
        {"id": "custom", "name": "Sistema Personalizado", "description": "Ideias originais, multi-unidades/franquias, workflows customizados, integracoes sob medida."},
    ],
    "process_steps": [
        {"step": 1, "name": "Descreva sua ideia", "description": "Texto ou audio — a IA transcreve.", "free": True},
        {"step": 2, "name": "Perfil da empresa", "description": "Informacoes do centro automotivo.", "free": True},
        {"step": 3, "name": "Diagnostico completo", "description": "Questionario detalhado + especificacao tecnica + estimativa de investimento.", "free": True},
        {"step": 4, "name": "Demo gratuita do MVP", "description": "7 dias de acesso ao workspace, sem cartao, sem compromisso.", "free": True},
        {"step": 5, "name": "Decisao", "description": "Seguir individualmente, formar cooperativa, ou recomecar.", "free": True},
        {"step": 6, "name": "Criacao do sistema", "description": "Equipe de engenheiros e especialistas constroem seu sistema.", "free": False},
        {"step": 7, "name": "Suporte e evolucao", "description": "Plano mensal de suporte com evolucao continua.", "free": False},
    ],
}

COOPERATIVE_MODEL = {
    "name": "Modelo Cooperativo",
    "description": "Grupos de centros automotivos compartilham o custo de desenvolvimento, reduzindo significativamente o investimento individual. Quanto mais membros, maior o desconto. Valores definidos na consulta.",
    "max_members": 10,
    "rules": [
        "Funcionalidades core sao compartilhadas entre o grupo",
        "Funcionalidades exclusivas sao add-on pago",
        "Cada membro mantem seus dados isolados",
        "Desconto aplicado sobre a mensalidade por membro",
    ],
}

MONETIZE_PROGRAM = {
    "name": "Programa Monetize seu Sistema",
    "description": "Transforme o sistema que voce construiu com a Pitcore em uma solucao comercializavel para outros centros automotivos.",
    "revenue_share": "Percentuais definidos contratualmente na consulta com especialista.",
    "eligibility_criteria": [
        "Resultados mensuraveis e documentados",
        "Arquitetura modular que permite replicacao",
        "Processo de negocio padronizavel para outros centros automotivos",
        "Dados estruturados com integridade operacional comprovada",
    ],
    "process_steps": [
        "Avaliacao tecnica — arquitetura, escalabilidade, fit de mercado",
        "Estruturacao comercial — posicionamento, publico-alvo, proposta de valor",
        "Padronizacao — adaptacao multi-tenant, documentacao, onboarding escalavel",
        "Definicao de participacao — termos contratuais, percentuais, responsabilidades",
        "Comercializacao conjunta — disponivel no ecossistema Pitcore",
    ],
    "pitcore_handles": [
        "Implementacao",
        "Infraestrutura",
        "Suporte",
        "Atualizacoes",
        "Evolucao tecnica",
    ],
    "disclaimers": [
        "Nao e modelo de investimento",
        "Nao ha garantia de volume de vendas ou retorno financeiro",
        "Sistema precisa ser aprovado em avaliacao tecnica",
        "Resultados dependem de fit de mercado, qualidade operacional e condicoes comerciais",
    ],
}

AUTOMOTIVE_SPECIALTIES = [
    "Mecanica Geral",
    "Funilaria e Pintura",
    "Eletrica Automotiva",
    "Ar Condicionado",
    "Suspensao e Freios",
    "Injecao Eletronica",
    "Cambio e Transmissao",
    "Pneus e Alinhamento",
    "Estetica Automotiva",
    "Blindagem",
    "Customizacao e Performance",
    "Diesel / Veiculos Pesados",
    "Motocicletas",
    "Hibridos e Eletricos",
]

DEMO_CONFIG = {
    "duration_days": 7,
    "max_work_orders": 20,
    "max_media_mb": 500,
    "requires_credit_card": False,
    "requires_commitment": False,
    "portal_url": "https://pitcore.online",
}

COMPANY_INFO = {
    "name": "Pitcore & Systems",
    "tagline": "Tecnologia premium para centros automotivos de alto padrao",
    "portal_url": "https://pitcore.online",
    "contact_email": "contato@pitcore.com.br",
    "positioning": "Nao somos uma agencia de software. Somos uma plataforma de produto que gera sistemas sob medida.",
    "values": [
        "Precisao",
        "Confiabilidade industrial",
        "Qualidade enterprise",
        "Valor premium",
    ],
}


def get_knowledge_base_text() -> str:
    """Return a formatted text version of the knowledge base for injection into prompts."""
    lines = []

    lines.append("=== BASE DE CONHECIMENTO PITCORE & SYSTEMS ===\n")

    # Agents
    lines.append("## AGENTES DE IA (Agent Overlay)\n")
    for agent in AGENTS:
        lines.append(f"### {agent['name']}")
        lines.append(f"{agent['description']}")
        lines.append("Funcionalidades:")
        for f in agent["features"]:
            lines.append(f"  - {f}")
        lines.append(f"Resultado: {agent['result']}")
        lines.append(f"Caso de uso: {agent['use_case']}")
        lines.append("")

    # Solution model
    lines.append("## MODELO DE SOLUCAO\n")
    lines.append("Nao existem pacotes pre-definidos. Cada solucao e montada sob medida")
    lines.append("com a combinacao de agentes mais adequada para o caso do cliente.")
    lines.append("A definicao e feita na consulta gratuita com especialista.")
    lines.append("")

    # Build
    lines.append("## BUILD SOB MEDIDA (valores sob consulta)\n")
    b = BUILD_SOB_MEDIDA
    lines.append(b["description"])
    lines.append("\nTipos de projeto:")
    for pt in b["project_types"]:
        lines.append(f"  - {pt['name']}: {pt['description']}")
    lines.append("\nProcesso (7 etapas):")
    for step in b["process_steps"]:
        free_tag = " [GRATUITO]" if step["free"] else " [PAGO]"
        lines.append(f"  {step['step']}. {step['name']}{free_tag} — {step['description']}")
    lines.append("")

    # Cooperative
    lines.append("## MODELO COOPERATIVO\n")
    c = COOPERATIVE_MODEL
    lines.append(c["description"])
    lines.append(f"Maximo de membros: {c['max_members']}")
    lines.append("")

    # Monetize
    lines.append("## PROGRAMA MONETIZE SEU SISTEMA\n")
    m = MONETIZE_PROGRAM
    lines.append(m["description"])
    lines.append(f"Participacao: {m['revenue_share']}")
    lines.append("Criterios de elegibilidade:")
    for cr in m["eligibility_criteria"]:
        lines.append(f"  - {cr}")
    lines.append("")

    # Specialties
    lines.append("## ESPECIALIDADES AUTOMOTIVAS ATENDIDAS\n")
    for i, spec in enumerate(AUTOMOTIVE_SPECIALTIES, 1):
        lines.append(f"  {i}. {spec}")
    lines.append("")

    # Demo
    lines.append("## DEMO GRATUITA\n")
    d = DEMO_CONFIG
    lines.append(f"Duracao: {d['duration_days']} dias")
    lines.append(f"Sem cartao de credito: {'Sim' if not d['requires_credit_card'] else 'Nao'}")
    lines.append(f"Sem compromisso: {'Sim' if not d['requires_commitment'] else 'Nao'}")
    lines.append(f"Portal: {d['portal_url']}")

    return "\n".join(lines)
