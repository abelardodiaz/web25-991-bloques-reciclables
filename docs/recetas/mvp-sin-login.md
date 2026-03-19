# Receta: MVP sin Login

> Con bloque-ui + bloque-api-client tienes un frontend rapido sin autenticacion.

---

## Bloques necesarios

```bash
# Backend
uv add bloque-core

# Frontend
pnpm add @bloque/ui @bloque/api-client
```

## Que obtienes

- Backend FastAPI minimo con health check
- Frontend Next.js con componentes shadcn/ui
- Cliente HTTP configurado para hablar con la API
- Sin auth, sin multitenant - lo minimo para un MVP

## Setup rapido

### Backend

```python
from fastapi import FastAPI
from bloque_core.middleware import RequestIDMiddleware
from bloque_core.health import health_router

app = FastAPI(title="MVP API")
app.add_middleware(RequestIDMiddleware)
app.include_router(health_router)

@app.get("/api/data")
async def get_data():
    return {"items": ["uno", "dos", "tres"]}
```

### Frontend

```tsx
import { ApiClient } from '@bloque/api-client'
import { Card, Button } from '@bloque/ui'

const api = new ApiClient({ baseURL: 'http://localhost:8000' })

export default async function Page() {
  const { data } = await api.get('/api/data')

  return (
    <div>
      {data.items.map((item: string) => (
        <Card key={item}>{item}</Card>
      ))}
    </div>
  )
}
```

## Cuando escalar

Cuando el MVP valide la idea, agregar bloques incrementalmente:

1. Necesitas login? -> `uv add bloque-auth` + `pnpm add @bloque/auth-react`
2. Necesitas multi-inquilino? -> `uv add bloque-multitenant`
3. Necesitas dashboard completo? -> `pnpm add @bloque/dashboard`

Los bloques se agregan sin reescribir lo existente.
