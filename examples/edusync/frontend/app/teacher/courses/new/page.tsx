"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { TextField } from "@ulfblk/forms";

export default function CreateCoursePage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const token = localStorage.getItem("edusync_token");
      const res = await fetch("/api/courses", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ title }),
      });

      if (res.ok) {
        setMessage("Curso creado exitosamente");
        setTimeout(() => router.push("/teacher"), 1500);
      } else {
        const err = await res.json().catch(() => ({ detail: "Error" }));
        setMessage(err.detail || "Error al crear curso");
      }
    } catch {
      setMessage("Error de conexion");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 500 }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>Crear nuevo curso</h1>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <TextField
            name="title"
            label="Titulo del curso"
            required
            value={title}
            onChange={(v) => setTitle(v)}
          />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <TextField
            name="description"
            label="Descripcion"
            value={description}
            onChange={(v) => setDescription(v)}
          />
        </div>

        {message && (
          <p style={{
            padding: "0.75rem", borderRadius: 6, marginBottom: "1rem",
            backgroundColor: message.includes("exitosamente") ? "#f0fdf4" : "#fef2f2",
            color: message.includes("exitosamente") ? "#16a34a" : "#dc2626",
          }}>
            {message}
          </p>
        )}

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "0.75rem 2rem", backgroundColor: "#2563eb", color: "#fff",
            border: "none", borderRadius: 6, cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Creando..." : "Crear curso"}
        </button>
      </form>
    </div>
  );
}
