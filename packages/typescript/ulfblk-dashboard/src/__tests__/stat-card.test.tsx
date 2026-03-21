import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatCard } from "../data/stat-card.js";

describe("StatCard", () => {
  it("renders label and value", () => {
    render(<StatCard label="Revenue" value="$12,345" />);

    expect(screen.getByText("Revenue")).toBeDefined();
    expect(screen.getByText("$12,345")).toBeDefined();
  });

  it("renders trend when provided", () => {
    render(
      <StatCard
        label="Users"
        value={1234}
        trend={{ value: "+12%", direction: "up" }}
      />,
    );

    expect(screen.getByText("+12%")).toBeDefined();
  });

  it("renders icon when provided", () => {
    render(
      <StatCard label="Sales" value={99} icon={<span data-testid="icon">$</span>} />,
    );

    expect(screen.getByTestId("icon")).toBeDefined();
  });

  it("applies custom className", () => {
    const { container } = render(
      <StatCard label="Test" value={0} className="custom-card" />,
    );

    expect((container.firstChild as HTMLElement).className).toContain("custom-card");
  });
});
