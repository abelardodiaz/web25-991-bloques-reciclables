"use client";

import { useState, useEffect } from "react";

interface Course {
  id: number;
  title: string;
  status: string;
}

export default function TeacherDashboard() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchCourses() {
      try {
        const token = localStorage.getItem("edusync_token");
        const res = await fetch("/api/courses", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setCourses(data.items || data);
        }
      } catch {
        // Silent
      } finally {
        setLoading(false);
      }
    }
    fetchCourses();
  }, []);

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>Dashboard del instructor</h1>

      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "1rem", marginBottom: "2rem" }}>
        <div style={{ padding: "1.5rem", backgroundColor: "#f0f9ff", borderRadius: 8, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: "#2563eb" }}>
            {courses.length}
          </div>
          <div style={{ color: "#64748b" }}>Mis cursos</div>
        </div>
        <div style={{ padding: "1.5rem", backgroundColor: "#f0fdf4", borderRadius: 8, textAlign: "center" }}>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: "#16a34a" }}>
            {courses.filter(c => c.status === "published").length}
          </div>
          <div style={{ color: "#64748b" }}>Publicados</div>
        </div>
      </div>

      {/* Course table */}
      <h2 style={{ fontSize: "1.2rem", marginBottom: "0.5rem" }}>Mis cursos</h2>
      {loading ? (
        <p style={{ color: "#888" }}>Cargando...</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid #e2e8f0", textAlign: "left" }}>
              <th style={{ padding: "0.75rem" }}>ID</th>
              <th style={{ padding: "0.75rem" }}>Titulo</th>
              <th style={{ padding: "0.75rem" }}>Estado</th>
            </tr>
          </thead>
          <tbody>
            {courses.map((c) => (
              <tr key={c.id} style={{ borderBottom: "1px solid #e2e8f0" }}>
                <td style={{ padding: "0.75rem" }}>{c.id}</td>
                <td style={{ padding: "0.75rem" }}>{c.title}</td>
                <td style={{ padding: "0.75rem" }}>{c.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
