import { useState, type ReactNode } from "react";
import { cn } from "@bloque/ui";
import type { PaginatedResponse } from "@bloque/types";

export type SortDirection = "asc" | "desc";

export interface ColumnDef<T> {
  key: keyof T & string;
  header: string;
  sortable?: boolean;
  render?: (value: T[keyof T], row: T) => ReactNode;
  className?: string;
}

export interface DataTableProps<T> {
  columns: ColumnDef<T>[];
  data: T[] | PaginatedResponse<T>;
  rowKey?: keyof T & string;
  onSort?: (key: string, direction: SortDirection) => void;
  onPageChange?: (page: number) => void;
  emptyMessage?: string;
  className?: string;
}

function isPaginated<T>(data: T[] | PaginatedResponse<T>): data is PaginatedResponse<T> {
  return !Array.isArray(data) && "items" in data && "pages" in data;
}

export function DataTable<T>({
  columns,
  data,
  rowKey = "id" as keyof T & string,
  onSort,
  onPageChange,
  emptyMessage = "No data available",
  className,
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<SortDirection>("asc");

  const rows = isPaginated(data) ? data.items : data;
  const pagination = isPaginated(data) ? data : null;

  function handleSort(key: string) {
    const newDir = sortKey === key && sortDir === "asc" ? "desc" : "asc";
    setSortKey(key);
    setSortDir(newDir);
    onSort?.(key, newDir);
  }

  return (
    <div className={cn("w-full overflow-auto", className)}>
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b border-[hsl(var(--bloque-border))]">
            {columns.map((col) => (
              <th
                key={col.key}
                className={cn(
                  "px-4 py-3 text-left font-medium text-[hsl(var(--bloque-muted-foreground))]",
                  col.sortable && "cursor-pointer select-none",
                  col.className,
                )}
                onClick={col.sortable ? () => handleSort(col.key) : undefined}
                aria-sort={
                  sortKey === col.key
                    ? sortDir === "asc"
                      ? "ascending"
                      : "descending"
                    : undefined
                }
              >
                <span className="flex items-center gap-1">
                  {col.header}
                  {col.sortable && sortKey === col.key && (
                    <span aria-hidden="true">
                      {sortDir === "asc" ? "^" : "v"}
                    </span>
                  )}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                className="px-4 py-8 text-center text-[hsl(var(--bloque-muted-foreground))]"
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            rows.map((row) => (
              <tr
                key={String(row[rowKey])}
                className="border-b border-[hsl(var(--bloque-border))] hover:bg-[hsl(var(--bloque-muted))]"
              >
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className={cn(
                      "px-4 py-3 text-[hsl(var(--bloque-foreground))]",
                      col.className,
                    )}
                  >
                    {col.render
                      ? col.render(row[col.key], row)
                      : String(row[col.key] ?? "")}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
      {pagination && pagination.pages > 1 && (
        <div className="flex items-center justify-between border-t border-[hsl(var(--bloque-border))] px-4 py-3">
          <p className="text-sm text-[hsl(var(--bloque-muted-foreground))]">
            Page {pagination.page} of {pagination.pages} ({pagination.total} total)
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={pagination.page <= 1}
              onClick={() => onPageChange?.(pagination.page - 1)}
              className="rounded-md border border-[hsl(var(--bloque-border))] px-3 py-1 text-sm disabled:opacity-50"
            >
              Previous
            </button>
            <button
              type="button"
              disabled={pagination.page >= pagination.pages}
              onClick={() => onPageChange?.(pagination.page + 1)}
              className="rounded-md border border-[hsl(var(--bloque-border))] px-3 py-1 text-sm disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
