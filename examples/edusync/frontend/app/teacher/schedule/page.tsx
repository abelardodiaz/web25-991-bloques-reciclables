"use client";

import { useState, useEffect, useCallback } from "react";
import { DaySelector, SlotPicker } from "@ulfblk/calendar-ui";
import type { Slot } from "@ulfblk/calendar-ui";
import { useCalendar } from "@ulfblk/calendar-ui";

function formatDate(d: Date): string {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export default function TeacherSchedule() {
  const { currentDate, setDate } = useCalendar(new Date());
  const [slots, setSlots] = useState<Slot[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchSlots = useCallback(async (date: Date) => {
    setLoading(true);
    try {
      const token = localStorage.getItem("edusync_token");
      const dateStr = formatDate(date);
      const res = await fetch(`/api/sessions/slots/instructor-1/${dateStr}`, {
        headers: { Authorization: `Bearer ${token || ""}` },
      });
      if (res.ok) {
        setSlots(await res.json());
      } else {
        setSlots([]);
      }
    } catch {
      setSlots([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSlots(currentDate);
  }, [currentDate, fetchSlots]);

  const available = slots.filter(s => s.available);
  const booked = slots.filter(s => !s.available);

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>Mi horario</h1>

      <div style={{ marginBottom: "1.5rem" }}>
        <DaySelector
          currentDate={currentDate}
          onChange={setDate}
          prevLabel="Anterior"
          nextLabel="Siguiente"
          todayLabel="Hoy"
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.5rem" }}>
        <div style={{ padding: "1rem", backgroundColor: "#f0fdf4", borderRadius: 8, textAlign: "center" }}>
          <strong>{available.length}</strong> slots disponibles
        </div>
        <div style={{ padding: "1rem", backgroundColor: "#fef2f2", borderRadius: 8, textAlign: "center" }}>
          <strong>{booked.length}</strong> slots ocupados
        </div>
      </div>

      {loading ? (
        <p style={{ color: "#888" }}>Cargando horario...</p>
      ) : (
        <SlotPicker
          slots={slots}
          onSelect={() => {}}
          emptyLabel="No hay slots configurados para este dia"
        />
      )}
    </div>
  );
}
