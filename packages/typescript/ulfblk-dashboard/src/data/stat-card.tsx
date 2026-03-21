import type { ReactNode } from "react";
import { cn } from "@ulfblk/ui";

export type TrendDirection = "up" | "down" | "neutral";

export interface StatCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  trend?: {
    value: string | number;
    direction: TrendDirection;
  };
  className?: string;
}

const trendColors: Record<TrendDirection, string> = {
  up: "text-green-600",
  down: "text-red-600",
  neutral: "text-[hsl(var(--bloque-muted-foreground))]",
};

const trendArrows: Record<TrendDirection, string> = {
  up: "^",
  down: "v",
  neutral: "-",
};

export function StatCard({
  label,
  value,
  icon,
  trend,
  className,
}: StatCardProps) {
  return (
    <div
      className={cn(
        "rounded-lg border border-[hsl(var(--bloque-border))] bg-[hsl(var(--bloque-card))] p-6",
        className,
      )}
    >
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-[hsl(var(--bloque-muted-foreground))]">
          {label}
        </p>
        {icon && (
          <span className="flex h-5 w-5 items-center justify-center text-[hsl(var(--bloque-muted-foreground))]">
            {icon}
          </span>
        )}
      </div>
      <div className="mt-2 flex items-baseline gap-2">
        <p className="text-2xl font-bold text-[hsl(var(--bloque-foreground))]">
          {value}
        </p>
        {trend && (
          <span className={cn("flex items-center gap-0.5 text-xs font-medium", trendColors[trend.direction])}>
            <span aria-hidden="true">{trendArrows[trend.direction]}</span>
            {trend.value}
          </span>
        )}
      </div>
    </div>
  );
}
