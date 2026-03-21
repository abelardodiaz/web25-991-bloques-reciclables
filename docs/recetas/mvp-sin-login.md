# Receta: MVP sin Login

> Con ulfblk-core + @ulfblk/api-client tienes un fullstack rapido sin autenticacion.

---

## Bloques necesarios

```bash
# Backend
uv add ulfblk-core

# Frontend
pnpm add @ulfblk/ui @ulfblk/api-client
```

## Que obtienes

- Backend FastAPI con health check y middleware
- Frontend con componentes UI y cliente HTTP
- Sin auth, sin multitenant - lo minimo para validar una idea

## Backend

```python
from ulfblk_core import create_app

app = create_app(service_name="mvp", version="0.1.0", title="MVP API")

@app.get("/api/data")
async def get_data():
    return {"items": ["uno", "dos", "tres"]}
```

## Frontend

```tsx
import { ApiClient } from "@ulfblk/api-client";

const api = new ApiClient({ baseURL: "http://localhost:8000" });

export default async function Page() {
  const { data } = await api.get("/api/data");

  return (
    <ul>
      {data.items.map((item: string) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}
```

## Cuando escalar

Cuando el MVP valide la idea, agregar bloques incrementalmente:

1. Necesitas login? -> `uv add ulfblk-auth` + `pnpm add @ulfblk/auth-react`
2. Necesitas base de datos? -> `uv add ulfblk-db`
3. Necesitas multi-inquilino? -> `uv add ulfblk-multitenant`
4. Necesitas dashboard? -> `pnpm add @ulfblk/dashboard`

Los bloques se agregan sin reescribir lo existente.
