"use client";

import { useState, useEffect } from "react";

interface Enrollment {
  id: number;
  course_id: number;
  student_id: string;
  status: string;
}

export default function StudentDashboard() {
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const token = localStorage.getItem("edusync_token");
        const res = await fetch("/api/enrollments", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setEnrollments(data.items || data);
        }
      } catch {
        // Silent fail
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>Mi Dashboard</h1>

      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem", marginBottom: "2rem" }}>
        <div style={{ padding: "1.5rem", backgroundColor: "#f0f9ff", borderRadius: 8, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: "#2563eb" }}>
            {enrollments.length}
          </div>
          <div style={{ color: "#64748b" }}>Cursos inscritos</div>
        </div>
        <div style={{ padding: "1.5rem", backgroundColor: "#f0fdf4", borderRadius: 8, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: "#16a34a" }}>
            {enrollments.filter(e => e.status === "completed").length}
          </div>
          <div style={{ color: "#64748b" }}>Completados</div>
        </div>
        <div style={{ padding: "1.5rem", backgroundColor: "#fefce8", borderRadius: 8, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: "#ca8a04" }}>
            {enrollments.filter(e => e.status === "active").length}
          </div>
          <div style={{ color: "#64748b" }}>En progreso</div>
        </div>
      </div>

      {/* Enrollment list */}
      <h2 style={{ fontSize: "1.2rem", marginBottom: "0.5rem" }}>Mis cursos</h2>
      {loading ? (
        <p style={{ color: "#888" }}>Cargando...</p>
      ) : enrollments.length === 0 ? (
        <p style={{ color: "#888" }}>No estas inscrito en ningun curso.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          {enrollments.map((e) => (
            <div
              key={e.id}
              style={{
                padding: "1rem", border: "1px solid #e2e8f0", borderRadius: 6,
                display: "flex", justifyContent: "space-between", alignItems: "center",
              }}
            >
              <span>Curso #{e.course_id}</span>
              <span style={{
                padding: "0.25rem 0.75rem", borderRadius: 12, fontSize: "0.85rem",
                backgroundColor: e.status === "completed" ? "#dcfce7" : "#fef9c3",
                color: e.status === "completed" ? "#16a34a" : "#ca8a04",
              }}>
                {e.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
