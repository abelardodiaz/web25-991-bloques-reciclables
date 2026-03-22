"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function TeacherLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("edusync_token");
    const role = localStorage.getItem("edusync_role");
    if (!token || (role !== "instructor" && role !== "admin")) {
      router.push("/login");
      return;
    }
    setAuthorized(true);
  }, [router]);

  if (!authorized) return null;

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <nav style={{
        width: 220, backgroundColor: "#1e293b", color: "#fff",
        padding: "1.5rem 1rem", display: "flex", flexDirection: "column", gap: "0.5rem",
      }}>
        <h2 style={{ fontSize: "1.2rem", marginBottom: "1rem" }}>EduSync - Instructor</h2>
        <Link href="/teacher" style={{ color: "#94a3b8", textDecoration: "none", padding: "0.5rem" }}>
          Dashboard
        </Link>
        <Link href="/teacher/courses/new" style={{ color: "#94a3b8", textDecoration: "none", padding: "0.5rem" }}>
          Crear curso
        </Link>
        <Link href="/teacher/schedule" style={{ color: "#94a3b8", textDecoration: "none", padding: "0.5rem" }}>
          Mi horario
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
      <main style={{ flex: 1, padding: "2rem" }}>
        {children}
      </main>
    </div>
  );
}
