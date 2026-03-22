"use client";

import Link from "next/link";

export default function HomePage() {
  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: "3rem 1rem", textAlign: "center" }}>
      <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>EduSync</h1>
      <p style={{ color: "#666", marginBottom: "2rem" }}>
        Plataforma educativa SaaS - 17 bloques ulfblk
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem", maxWidth: 300, margin: "0 auto" }}>
        <Link
          href="/login"
          style={{
            display: "block", padding: "0.75rem", backgroundColor: "#2563eb",
            color: "#fff", borderRadius: 6, textDecoration: "none", textAlign: "center",
          }}
        >
          Iniciar sesion
        </Link>
        <Link
          href="/admin"
          style={{
            display: "block", padding: "0.75rem", backgroundColor: "#6b7280",
            color: "#fff", borderRadius: 6, textDecoration: "none", textAlign: "center",
          }}
        >
          Panel de administracion
        </Link>
      </div>
    </div>
  );
}
