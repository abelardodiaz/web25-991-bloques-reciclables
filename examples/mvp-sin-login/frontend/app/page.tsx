"use client";

import { useEffect, useState } from "react";

interface DataResponse {
  items: string[];
}

export default function Page() {
  const [items, setItems] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/data")
      .then((res) => res.json())
      .then((data: DataResponse) => {
        setItems(data.items);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Cargando...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>MVP sin Login</h1>
      <p>Datos desde el backend (ulfblk-core):</p>
      <ul>
        {items.map((item) => (
          <li key={item} style={{ fontSize: "1.2rem", margin: "0.5rem 0" }}>
            {item}
          </li>
        ))}
      </ul>
      <hr style={{ margin: "2rem 0" }} />
      <p style={{ color: "#666" }}>
        Backend: ulfblk-core | Frontend: Next.js + @ulfblk/api-client
      </p>
    </main>
  );
}
