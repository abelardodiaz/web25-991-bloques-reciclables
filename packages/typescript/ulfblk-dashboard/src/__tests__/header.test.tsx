import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { DashboardProvider } from "../context/dashboard-context.js";
import { Header } from "../layout/header.js";

function renderWithProvider(ui: React.ReactNode) {
  return render(
    <DashboardProvider>{ui}</DashboardProvider>,
  );
}

describe("Header", () => {
  it("renders breadcrumbs slot", () => {
    renderWithProvider(
      <Header breadcrumbs={<span>Home / Dashboard</span>} />,
    );

    expect(screen.getByText("Home / Dashboard")).toBeDefined();
  });

  it("renders actions slot", () => {
    renderWithProvider(
      <Header actions={<button type="button">New</button>} />,
    );

    expect(screen.getByText("New")).toBeDefined();
  });

  it("renders mobile menu toggle button", () => {
    renderWithProvider(<Header />);

    expect(screen.getByLabelText("Toggle menu")).toBeDefined();
  });
});
