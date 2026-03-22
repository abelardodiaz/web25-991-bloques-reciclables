"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { TextField } from "@ulfblk/forms";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [tenantId, setTenantId] = useState("acme");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, tenant_id: tenantId }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Error de autenticacion" }));
        setError(err.detail || "Credenciales invalidas");
        setLoading(false);
        return;
      }

      const data = await res.json();
      // Store token and role in localStorage
      localStorage.setItem("edusync_token", data.access_token);
      localStorage.setItem("edusync_role", data.role);
      localStorage.setItem("edusync_tenant", data.tenant_id);

      // Redirect based on role
      if (data.role === "admin") {
        router.push("/admin");
      } else if (data.role === "instructor") {
        router.push("/teacher");
      } else {
        router.push("/student");
      }
    } catch {
      setError("Error de conexion");
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: "0 auto", padding: "3rem 1rem" }}>
      <h1 style={{ textAlign: "center", marginBottom: "2rem" }}>Iniciar sesion</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <TextField
            name="username"
            label="Usuario"
            required
            value={username}
            onChange={(v) => setUsername(v)}
          />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <TextField
            name="tenant"
            label="Organizacion"
            required
            value={tenantId}
            onChange={(v) => setTenantId(v)}
          />
        </div>
        {error && (
          <p style={{ color: "#dc2626", marginBottom: "1rem", textAlign: "center" }}>{error}</p>
        )}
        <button
          type="submit"
          disabled={loading}
          style={{
            width: "100%", padding: "0.75rem", backgroundColor: "#2563eb",
            color: "#fff", border: "none", borderRadius: 6, fontSize: "1rem",
            cursor: loading ? "not-allowed" : "pointer", opacity: loading ? 0.6 : 1,
          }}
        >
          {loading ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}
