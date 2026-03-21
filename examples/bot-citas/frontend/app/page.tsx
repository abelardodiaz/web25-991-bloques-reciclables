"use client";

import { useState, useEffect, useCallback } from "react";
import { DaySelector, SlotPicker } from "@ulfblk/calendar-ui";
import type { Slot } from "@ulfblk/calendar-ui";
import { useCalendar } from "@ulfblk/calendar-ui";

interface BookingForm {
  name: string;
  phone: string;
}

type PageState = "selecting" | "form" | "submitting" | "confirmed" | "error";

function formatDate(d: Date): string {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function formatTime(isoString: string): string {
  const d = new Date(isoString);
  return d.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" });
}

export default function BookingPage() {
  const { currentDate, setDate } = useCalendar(new Date());
  const [slots, setSlots] = useState<Slot[]>([]);
  const [selectedSlot, setSelectedSlot] = useState<Slot | undefined>(undefined);
  const [form, setForm] = useState<BookingForm>({ name: "", phone: "" });
  const [pageState, setPageState] = useState<PageState>("selecting");
  const [errorMsg, setErrorMsg] = useState("");
  const [loadingSlots, setLoadingSlots] = useState(false);

  const fetchSlots = useCallback(async (date: Date) => {
    setLoadingSlots(true);
    setSelectedSlot(undefined);
    setPageState("selecting");
    try {
      const dateStr = formatDate(date);
      const res = await fetch(`/api/slots/${dateStr}`);
      if (!res.ok) {
        setSlots([]);
        return;
      }
      const data: Slot[] = await res.json();
      setSlots(data);
    } catch {
      setSlots([]);
    } finally {
      setLoadingSlots(false);
    }
  }, []);

  useEffect(() => {
    fetchSlots(currentDate);
  }, [currentDate, fetchSlots]);

  function handleDateChange(date: Date) {
    setDate(date);
  }

  function handleSlotSelect(slot: Slot) {
    if (!slot.available) return;
    setSelectedSlot(slot);
    setPageState("form");
    setErrorMsg("");
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedSlot) return;

    setPageState("submitting");
    setErrorMsg("");

    const startDate = new Date(selectedSlot.start);
    const dateStr = formatDate(startDate);
    const hours = String(startDate.getUTCHours()).padStart(2, "0");
    const minutes = String(startDate.getUTCMinutes()).padStart(2, "0");
    const timeStr = `${hours}:${minutes}`;

    try {
      const res = await fetch("/api/appointments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          date: dateStr,
          time: timeStr,
          name: form.name,
          phone: form.phone,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Error al crear la cita" }));
        setErrorMsg(err.detail || "Error al crear la cita");
        setPageState("error");
        return;
      }

      setPageState("confirmed");
    } catch {
      setErrorMsg("Error de conexion. Intente de nuevo.");
      setPageState("error");
    }
  }

  function handleReset() {
    setSelectedSlot(undefined);
    setForm({ name: "", phone: "" });
    setPageState("selecting");
    setErrorMsg("");
    fetchSlots(currentDate);
  }

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ textAlign: "center", marginBottom: "0.5rem" }}>
        Reservar Cita
      </h1>
      <p style={{ textAlign: "center", color: "#666", marginBottom: "2rem" }}>
        Selecciona un dia y horario disponible
      </p>

      {/* Day selector */}
      <div style={{ marginBottom: "1.5rem" }}>
        <DaySelector
          currentDate={currentDate}
          onChange={handleDateChange}
          prevLabel="Anterior"
          nextLabel="Siguiente"
          todayLabel="Hoy"
        />
      </div>

      {/* Slot picker */}
      {loadingSlots ? (
        <p style={{ textAlign: "center", color: "#888" }}>Cargando horarios...</p>
      ) : (
        <div style={{ marginBottom: "1.5rem" }}>
          <SlotPicker
            slots={slots}
            onSelect={handleSlotSelect}
            selectedSlot={selectedSlot}
            emptyLabel="No hay horarios disponibles para este dia"
          />
        </div>
      )}

      {/* Booking form */}
      {(pageState === "form" || pageState === "submitting") && selectedSlot && (
        <div
          style={{
            border: "1px solid #ddd",
            borderRadius: 8,
            padding: "1.5rem",
            marginTop: "1rem",
          }}
        >
          <h2 style={{ marginBottom: "0.5rem" }}>Datos para la cita</h2>
          <p style={{ color: "#555", marginBottom: "1rem" }}>
            Horario: {formatTime(selectedSlot.start)} - {formatTime(selectedSlot.end)}
          </p>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: "1rem" }}>
              <label
                htmlFor="name"
                style={{ display: "block", marginBottom: 4, fontWeight: 600 }}
              >
                Nombre completo
              </label>
              <input
                id="name"
                type="text"
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  border: "1px solid #ccc",
                  borderRadius: 4,
                  fontSize: "1rem",
                }}
              />
            </div>
            <div style={{ marginBottom: "1rem" }}>
              <label
                htmlFor="phone"
                style={{ display: "block", marginBottom: 4, fontWeight: 600 }}
              >
                Telefono
              </label>
              <input
                id="phone"
                type="tel"
                required
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  border: "1px solid #ccc",
                  borderRadius: 4,
                  fontSize: "1rem",
                }}
              />
            </div>
            <button
              type="submit"
              disabled={pageState === "submitting"}
              style={{
                width: "100%",
                padding: "0.75rem",
                backgroundColor: "#2563eb",
                color: "#fff",
                border: "none",
                borderRadius: 4,
                fontSize: "1rem",
                cursor: pageState === "submitting" ? "not-allowed" : "pointer",
                opacity: pageState === "submitting" ? 0.6 : 1,
              }}
            >
              {pageState === "submitting" ? "Reservando..." : "Confirmar Cita"}
            </button>
          </form>
        </div>
      )}

      {/* Error message */}
      {pageState === "error" && (
        <div
          style={{
            border: "1px solid #ef4444",
            borderRadius: 8,
            padding: "1.5rem",
            marginTop: "1rem",
            backgroundColor: "#fef2f2",
            textAlign: "center",
          }}
        >
          <p style={{ color: "#dc2626", marginBottom: "1rem" }}>{errorMsg}</p>
          <button
            onClick={handleReset}
            style={{
              padding: "0.5rem 1.5rem",
              backgroundColor: "#ef4444",
              color: "#fff",
              border: "none",
              borderRadius: 4,
              cursor: "pointer",
            }}
          >
            Intentar de nuevo
          </button>
        </div>
      )}

      {/* Confirmation */}
      {pageState === "confirmed" && selectedSlot && (
        <div
          style={{
            border: "1px solid #22c55e",
            borderRadius: 8,
            padding: "1.5rem",
            marginTop: "1rem",
            backgroundColor: "#f0fdf4",
            textAlign: "center",
          }}
        >
          <h2 style={{ color: "#16a34a", marginBottom: "0.5rem" }}>
            Cita confirmada
          </h2>
          <p style={{ marginBottom: "0.25rem" }}>
            <strong>{form.name}</strong>
          </p>
          <p style={{ marginBottom: "0.25rem" }}>
            {formatDate(currentDate)} a las {formatTime(selectedSlot.start)}
          </p>
          <p style={{ color: "#555", marginBottom: "1rem" }}>
            Tel: {form.phone}
          </p>
          <button
            onClick={handleReset}
            style={{
              padding: "0.5rem 1.5rem",
              backgroundColor: "#22c55e",
              color: "#fff",
              border: "none",
              borderRadius: 4,
              cursor: "pointer",
            }}
          >
            Reservar otra cita
          </button>
        </div>
      )}
    </div>
  );
}
