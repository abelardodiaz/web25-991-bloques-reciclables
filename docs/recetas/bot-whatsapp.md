# Receta: Bot de WhatsApp

> Con bloque-core + bloque-channels + bloque-ai construyes un bot conversacional.

---

## Bloques necesarios

```bash
uv add bloque-core bloque-channels bloque-ai-rag
```

## Que obtienes

- API FastAPI con webhook processing
- Integracion WhatsApp via Meta Cloud API
- Pipeline de procesamiento de mensajes
- RAG con ChromaDB para respuestas contextuales
- LLM gateway (DeepSeek, OpenAI, Ollama)
- Logging estructurado de conversaciones

## Setup rapido

```python
from fastapi import FastAPI
from bloque_core.middleware import RequestIDMiddleware
from bloque_core.logging import setup_logging
from bloque_channels.whatsapp import WhatsAppRouter
from bloque_ai_rag.pipeline import RAGPipeline

app = FastAPI(title="Bot WhatsApp")
setup_logging()
app.add_middleware(RequestIDMiddleware)

# Configurar RAG
rag = RAGPipeline(
    collection="knowledge_base",
    llm_provider="deepseek",
)

# Webhook WhatsApp
whatsapp = WhatsAppRouter(
    verify_token="mi-token-verificacion",
    on_message=lambda msg: rag.respond(msg.text),
)

app.include_router(whatsapp.router, prefix="/webhook")
```

## Variables de entorno

```env
WHATSAPP_TOKEN=...
WHATSAPP_VERIFY_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
LLM_API_KEY=...
```

## Agregar multitenant (opcional)

Si el bot sirve a multiples negocios:

```bash
uv add bloque-auth bloque-multitenant
```

Cada tenant tiene su propia coleccion en ChromaDB y sus propias credenciales de WhatsApp (via TenantCredential).
