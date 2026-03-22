"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface Course {
  id: number;
  title: string;
  description: string | null;
  instructor_id: string;
  status: string;
}

export default function CourseCatalog() {
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
        // Silent fail
      } finally {
        setLoading(false);
      }
    }
    fetchCourses();
  }, []);

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>Catalogo de cursos</h1>
      {loading ? (
        <p style={{ color: "#888" }}>Cargando cursos...</p>
      ) : courses.length === 0 ? (
        <p style={{ color: "#888" }}>No hay cursos disponibles.</p>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "1rem" }}>
          {courses.map((course) => (
            <Link
              key={course.id}
              href={`/student/courses/${course.id}`}
              style={{ textDecoration: "none", color: "inherit" }}
            >
              <div style={{
                padding: "1.5rem", border: "1px solid #e2e8f0", borderRadius: 8,
                transition: "box-shadow 0.2s",
              }}>
                <h3 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>{course.title}</h3>
                <p style={{ color: "#64748b", fontSize: "0.9rem" }}>
                  {course.description || "Sin descripcion"}
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
