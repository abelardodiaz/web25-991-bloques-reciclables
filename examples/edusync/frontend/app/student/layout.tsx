"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function StudentLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("edusync_token");
    if (!token) {
      router.push("/login");
      return;
    }
    setAuthorized(true);
  }, [router]);

  if (!authorized) return null;

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {/* Sidebar */}
      <nav style={{
        width: 220, backgroundColor: "#1e293b", color: "#fff",
        padding: "1.5rem 1rem", display: "flex", flexDirection: "column", gap: "0.5rem",
      }}>
        <h2 style={{ fontSize: "1.2rem", marginBottom: "1rem" }}>EduSync</h2>
        <Link href="/student" style={{ color: "#94a3b8", textDecoration: "none", padding: "0.5rem" }}>
          Dashboard
        </Link>
        <Link href="/student/courses" style={{ color: "#94a3b8", textDecoration: "none", padding: "0.5rem" }}>
          Cursos
        </Link>
        <Link href="/student/schedule" style={{ color: "#94a3b8", textDecoration: "none", padding: "0.5rem" }}>
          Horarios
        </Link>
        <div style={{ marginTop: "auto" }}>
          <button
            onClick={() => { localStorage.clear(); router.push("/login"); }}
            style={{
              background: "none", border: "none", color: "#94a3b8",
              cursor: "pointer", padding: "0.5rem",
            }}
          >
            Cerrar sesion
          </button>
        </div>
      </nav>
      {/* Content */}
      <main style={{ flex: 1, padding: "2rem" }}>
        {children}
      </main>
    </div>
  );
}
