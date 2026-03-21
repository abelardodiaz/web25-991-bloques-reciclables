/**
 * MVP sin Login - Frontend page.
 * Based on docs/recetas/mvp-sin-login.md
 */

import { BloqueClient } from "@ulfblk/api-client";

const api = new BloqueClient({ baseUrl: "http://localhost:8000" });

interface DataResponse {
  items: string[];
}

export default async function Page() {
  const response = await api.get<DataResponse>("/api/data");

  return (
    <ul>
      {response.items.map((item: string) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}
