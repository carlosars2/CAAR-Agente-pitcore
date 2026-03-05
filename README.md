# CAAR — Agente de IA Pitcore & Systems

Agente de IA para atendimento inteligente de centros automotivos.
Funciona como primeiro ponto de contato no site e via WhatsApp.

## Stack

- **Python 3.11** + **FastAPI** (API gateway)
- **LangChain + LangGraph** (orquestracao do agente)
- **Claude Sonnet 4.6** via Anthropic API (LLM)
- **Redis** (memoria de conversa)
- **Evolution API** (WhatsApp self-hosted)

## Setup Rapido

```bash
# 1. Clonar
git clone https://github.com/carlosars2/CAAR-Agente-pitcore.git
cd CAAR-Agente-pitcore

# 2. Configurar
cp .env.example .env
# Editar .env com suas chaves (ANTHROPIC_API_KEY, EVOLUTION_API_KEY, etc.)

# 3. Rodar com Docker
docker compose -f docker/docker-compose.prod.yml up -d

# OU rodar localmente
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

## Endpoints

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/api/health` | Health check |
| POST | `/api/chat/message` | Enviar mensagem (REST) |
| WS | `/api/chat/ws/{conversation_id}` | Chat em tempo real (WebSocket) |
| POST | `/api/whatsapp/webhook` | Webhook da Evolution API |

## Widget do Site

Adicione ao HTML do `pitcore.online`:

```html
<link rel="stylesheet" href="https://pitcore.online/agent/widget/pitcore-chat.css">
<script src="https://pitcore.online/agent/widget/pitcore-chat.js"
        data-api="https://pitcore.online/agent/api"
        defer></script>
```

## Nginx (adicionar ao config existente)

```nginx
# CAAR Agent API
location /agent/api/ {
    proxy_pass http://localhost:8000/api/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 300s;
}

# Widget static files
location /agent/widget/ {
    alias /opt/caar-agent/widget/;
    expires 1d;
}
```

## Deploy na VPS

```bash
ssh -i ~/.ssh/pitcore_deploy root@187.77.229.18

cd /opt/caar-agent
git pull origin main
docker compose -f docker/docker-compose.prod.yml build caar-agent
docker compose -f docker/docker-compose.prod.yml up -d caar-agent
nginx -t && systemctl reload nginx
```

## Estrutura

```
src/
  agent/          # LangGraph state machine + tools
    prompts/      # System prompt + knowledge base
  api/            # FastAPI routes
  channels/       # Website + WhatsApp adapters
  memory/         # Redis conversation memory
  config/         # Settings
  models/         # Pydantic models
widget/           # Embeddable chat widget (JS + CSS)
docker/           # Dockerfile + compose
```
