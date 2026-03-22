"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { TextField } from "@ulfblk/forms";

interface Course {
  id: number;
  title: string;
  description: string | null;
}

interface Lesson {
  id: number;
  title: string;
  order: number;
  duration_minutes: number;
}

export default function CourseDetailPage() {
  const params = useParams();
  const courseId = params.id;
  const [course, setCourse] = useState<Course | null>(null);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [enrolled, setEnrolled] = useState(false);
  const [enrolling, setEnrolling] = useState(false);
  const [message, setMessage] = useState("");

  const token = typeof window !== "undefined" ? localStorage.getItem("edusync_token") : null;
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    async function fetchCourse() {
      try {
        const res = await fetch(`/api/courses/${courseId}`, { headers });
        if (res.ok) setCourse(await res.json());
      } catch {
        // Silent
      }
    }
    fetchCourse();
  }, [courseId]);

  async function handleEnroll() {
    setEnrolling(true);
    setMessage("");
    try {
      const res = await fetch("/api/enrollments", {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ course_id: Number(courseId), student_id: "current-user" }),
      });
      if (res.ok) {
        setEnrolled(true);
        setMessage("Inscripcion exitosa");
      } else {
        const err = await res.json().catch(() => ({ detail: "Error" }));
        setMessage(err.detail || "Error al inscribirse");
      }
    } catch {
      setMessage("Error de conexion");
    } finally {
      setEnrolling(false);
    }
  }

  if (!course) return <p style={{ color: "#888" }}>Cargando curso...</p>;

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>{course.title}</h1>
      <p style={{ color: "#64748b", marginBottom: "1.5rem" }}>
        {course.description || "Sin descripcion"}
      </p>

      {/* Enroll button */}
      {!enrolled && (
        <button
          onClick={handleEnroll}
          disabled={enrolling}
          style={{
            padding: "0.75rem 2rem", backgroundColor: "#2563eb", color: "#fff",
            border: "none", borderRadius: 6, cursor: enrolling ? "not-allowed" : "pointer",
            marginBottom: "1rem",
          }}
        >
          {enrolling ? "Inscribiendo..." : "Inscribirme"}
        </button>
      )}

      {message && (
        <p style={{
          padding: "0.75rem", borderRadius: 6, marginBottom: "1rem",
          backgroundColor: enrolled ? "#f0fdf4" : "#fef2f2",
          color: enrolled ? "#16a34a" : "#dc2626",
        }}>
          {message}
        </p>
      )}

      {/* Lessons */}
      <h2 style={{ fontSize: "1.2rem", marginBottom: "0.5rem" }}>Lecciones</h2>
      {lessons.length === 0 ? (
        <p style={{ color: "#888" }}>Las lecciones se mostraran al inscribirte.</p>
      ) : (
        <ol style={{ paddingLeft: "1.5rem" }}>
          {lessons.map((l) => (
            <li key={l.id} style={{ marginBottom: "0.5rem" }}>
              {l.title} ({l.duration_minutes} min)
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
