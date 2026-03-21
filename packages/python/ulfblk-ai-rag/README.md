# bloque-ai-rag

RAG pipeline: ChromaDB vector search + LLM gateway multi-provider (DeepSeek, OpenAI, Ollama).

## Instalacion

```bash
uv add bloque-ai-rag
```

## Uso rapido

```python
from bloque_ai_rag.pipeline import RAGPipeline

# Crear pipeline con ChromaDB + DeepSeek
rag = RAGPipeline(
    collection="knowledge_base",
    llm_provider="deepseek",
)

async with rag:
    # Ingestar documentos
    await rag.ingest([
        "FastAPI es un framework web moderno para Python.",
        "ChromaDB es una base de datos vectorial open source.",
    ])

    # Consultar
    response = await rag.respond("Que es FastAPI?")
    print(response.answer)
    print(response.contexts)  # documentos relevantes
```

## Providers soportados

| Provider | API Base | Modelo default |
|----------|----------|---------------|
| `deepseek` | `https://api.deepseek.com` | `deepseek-chat` |
| `openai` | `https://api.openai.com` | `gpt-4o-mini` |
| `ollama` | `http://localhost:11434` | `llama3.2` |

## Componentes

- **ChromaClient** - Cliente HTTP para ChromaDB REST API (sin deps pesadas)
- **OpenAICompatibleClient** - Cliente para DeepSeek, OpenAI, y cualquier API compatible
- **OllamaClient** - Cliente para Ollama local
- **RAGPipeline** - Orquestador: query -> vector search -> context building -> LLM generation

## Multitenant

Con `ulfblk-multitenant` instalado, las colecciones se prefijan automaticamente con el tenant_id:

```python
rag = RAGPipeline(collection="knowledge_base", llm_provider="deepseek")
# Con tenant "acme" activo -> coleccion "acme__knowledge_base"
```

## Dependencias

- `ulfblk-core` (logging, health checks)
- `httpx>=0.27` (HTTP client async)

No requiere el paquete `chromadb` (~200MB). Usa ChromaDB REST API directamente.
