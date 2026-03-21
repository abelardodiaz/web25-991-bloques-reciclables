# Receta: Bot de WhatsApp

> Con ulfblk-core + ulfblk-channels + ulfblk-ai-rag construyes un bot conversacional.

---

## Bloques necesarios

```bash
uv add ulfblk-core ulfblk-channels ulfblk-ai-rag
```

## Que obtienes

- API FastAPI con webhook processing
- Integracion WhatsApp via Meta Cloud API
- RAG con ChromaDB para respuestas contextuales
- LLM gateway (DeepSeek, OpenAI, Ollama)
- Logging estructurado de conversaciones

## Setup rapido

```python
from ulfblk_core import create_app, setup_logging
from ulfblk_channels.whatsapp import WhatsAppClient
from ulfblk_channels.models.settings import WhatsAppSettings
from ulfblk_ai_rag.pipeline import RAGPipeline

setup_logging()

app = create_app(service_name="bot-wa", version="0.1.0")

# Configurar WhatsApp
wa_settings = WhatsAppSettings()  # Lee BLOQUE_WHATSAPP_* de env
wa_client = WhatsAppClient(wa_settings)

# Configurar RAG
rag = RAGPipeline(
    collection="knowledge_base",
    llm_provider="deepseek",
)

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request):
    message = wa_client.receive(await request.json())
    if message:
        response = await rag.respond(message.text)
        await wa_client.send_text(message.sender, response)
    return {"status": "ok"}
```

## Variables de entorno

```env
BLOQUE_WHATSAPP_API_TOKEN=...
BLOQUE_WHATSAPP_VERIFY_TOKEN=...
BLOQUE_WHATSAPP_PHONE_NUMBER_ID=...
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
LLM_API_KEY=...
```

## Agregar multitenant (opcional)

Si el bot sirve a multiples negocios:

```bash
uv add ulfblk-auth ulfblk-multitenant
```

Cada tenant tiene su propia coleccion en ChromaDB y sus propias credenciales de WhatsApp.
