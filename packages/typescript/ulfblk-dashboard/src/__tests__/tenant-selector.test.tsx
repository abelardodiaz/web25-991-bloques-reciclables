import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { TenantSelector } from "../user/tenant-selector.js";

const tenants = [
  { id: "t1", name: "Acme Corp" },
  { id: "t2", name: "Globex Inc" },
  { id: "t3", name: "Initech" },
];

describe("TenantSelector", () => {
  it("renders nothing when tenants is empty", () => {
    const { container } = render(<TenantSelector tenants={[]} />);

    expect(container.innerHTML).toBe("");
  });

  it("shows current tenant name", () => {
    render(<TenantSelector tenants={tenants} currentTenantId="t2" />);

    expect(screen.getByText("Globex Inc")).toBeDefined();
  });

  it("opens dropdown and shows all tenants", () => {
    render(<TenantSelector tenants={tenants} currentTenantId="t1" />);

    fireEvent.click(screen.getByText("Acme Corp"));

    expect(screen.getByText("Globex Inc")).toBeDefined();
    expect(screen.getByText("Initech")).toBeDefined();
  });

  it("calls onSelect when a tenant is clicked", () => {
    const onSelect = vi.fn();
    render(
      <TenantSelector
        tenants={tenants}
        currentTenantId="t1"
        onSelect={onSelect}
      />,
    );

    fireEvent.click(screen.getByText("Acme Corp"));
    fireEvent.click(screen.getByText("Globex Inc"));

    expect(onSelect).toHaveBeenCalledWith("t2");
  });
});
