import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DashboardProvider } from "../context/dashboard-context.js";
import { Sidebar } from "../layout/sidebar.js";

function renderWithProvider(ui: React.ReactNode, defaultCollapsed = false) {
  return render(
    <DashboardProvider defaultCollapsed={defaultCollapsed}>
      {ui}
    </DashboardProvider>,
  );
}

describe("Sidebar", () => {
  it("renders children inside nav", () => {
    renderWithProvider(
      <Sidebar><span>nav-items</span></Sidebar>,
    );

    expect(screen.getByText("nav-items")).toBeDefined();
  });

  it("renders header slot", () => {
    renderWithProvider(
      <Sidebar header={<span>logo</span>}><span>nav</span></Sidebar>,
    );

    expect(screen.getByText("logo")).toBeDefined();
  });

  it("renders footer slot", () => {
    renderWithProvider(
      <Sidebar footer={<span>footer-content</span>}><span>nav</span></Sidebar>,
    );

    expect(screen.getByText("footer-content")).toBeDefined();
  });

  it("uses collapsed width when defaultCollapsed", () => {
    renderWithProvider(
      <Sidebar><span>nav</span></Sidebar>,
      true,
    );

    const aside = document.querySelector("aside");
    expect(aside?.style.width).toBe("4rem");
  });
});
