import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DataTable, type ColumnDef } from "../data/data-table.js";
import type { PaginatedResponse } from "@ulfblk/types";

interface TestRow {
  id: string;
  name: string;
  email: string;
}

const columns: ColumnDef<TestRow>[] = [
  { key: "name", header: "Name", sortable: true },
  { key: "email", header: "Email" },
];

const testData: TestRow[] = [
  { id: "1", name: "Alice", email: "alice@test.com" },
  { id: "2", name: "Bob", email: "bob@test.com" },
];

describe("DataTable", () => {
  it("renders rows from array data", () => {
    render(<DataTable columns={columns} data={testData} />);

    expect(screen.getByText("Alice")).toBeDefined();
    expect(screen.getByText("bob@test.com")).toBeDefined();
  });

  it("renders column headers", () => {
    render(<DataTable columns={columns} data={testData} />);

    expect(screen.getByText("Name")).toBeDefined();
    expect(screen.getByText("Email")).toBeDefined();
  });

  it("shows empty message when data is empty", () => {
    render(<DataTable columns={columns} data={[]} emptyMessage="Nothing here" />);

    expect(screen.getByText("Nothing here")).toBeDefined();
  });

  it("calls onSort when sortable column header is clicked", () => {
    const onSort = vi.fn();
    render(<DataTable columns={columns} data={testData} onSort={onSort} />);

    fireEvent.click(screen.getByText("Name"));
    expect(onSort).toHaveBeenCalledWith("name", "asc");

    fireEvent.click(screen.getByText("Name"));
    expect(onSort).toHaveBeenCalledWith("name", "desc");
  });

  it("renders pagination for PaginatedResponse", () => {
    const paginated: PaginatedResponse<TestRow> = {
      items: testData,
      total: 20,
      page: 2,
      pageSize: 10,
      pages: 2,
    };

    render(<DataTable columns={columns} data={paginated} />);

    expect(screen.getByText("Page 2 of 2 (20 total)")).toBeDefined();
  });

  it("calls onPageChange when pagination buttons are clicked", () => {
    const onPageChange = vi.fn();
    const paginated: PaginatedResponse<TestRow> = {
      items: testData,
      total: 30,
      page: 2,
      pageSize: 10,
      pages: 3,
    };

    render(<DataTable columns={columns} data={paginated} onPageChange={onPageChange} />);

    fireEvent.click(screen.getByText("Previous"));
    expect(onPageChange).toHaveBeenCalledWith(1);

    fireEvent.click(screen.getByText("Next"));
    expect(onPageChange).toHaveBeenCalledWith(3);
  });
});
