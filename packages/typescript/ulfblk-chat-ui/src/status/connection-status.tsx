"use client";

export interface ConnectionStatusProps {
  online: boolean;
  onlineLabel?: string;
  offlineLabel?: string;
}

export function ConnectionStatus({
  online,
  onlineLabel = "Conectado",
  offlineLabel = "Desconectado",
}: ConnectionStatusProps) {
  return (
    <div className="flex items-center gap-2 px-3 py-1">
      <span
        className={`inline-block h-2 w-2 rounded-full ${
          online ? "bg-green-500" : "bg-red-500"
        }`}
      />
      <span className="text-xs text-[hsl(var(--bloque-muted-foreground))]">
        {online ? onlineLabel : offlineLabel}
      </span>
    </div>
  );
}
