"use client";

import { useState, useCallback } from "react";

export interface UseCalendarReturn {
  currentDate: Date;
  goToNext: () => void;
  goToPrev: () => void;
  goToToday: () => void;
  setDate: (date: Date) => void;
}

export function useCalendar(initialDate?: Date): UseCalendarReturn {
  const [currentDate, setCurrentDate] = useState<Date>(
    initialDate ?? new Date(),
  );

  const goToNext = useCallback(() => {
    setCurrentDate((prev) => {
      const next = new Date(prev);
      next.setDate(next.getDate() + 1);
      return next;
    });
  }, []);

  const goToPrev = useCallback(() => {
    setCurrentDate((prev) => {
      const d = new Date(prev);
      d.setDate(d.getDate() - 1);
      return d;
    });
  }, []);

  const goToToday = useCallback(() => {
    setCurrentDate(new Date());
  }, []);

  const setDate = useCallback((date: Date) => {
    setCurrentDate(date);
  }, []);

  return { currentDate, goToNext, goToPrev, goToToday, setDate };
}
