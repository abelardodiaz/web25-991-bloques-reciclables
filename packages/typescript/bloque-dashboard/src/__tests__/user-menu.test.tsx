import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { UserMenu } from "../user/user-menu.js";

describe("UserMenu", () => {
  it("renders nothing when no user", () => {
    const { container } = render(<UserMenu />);

    expect(container.innerHTML).toBe("");
  });

  it("renders user initials avatar", () => {
    render(
      <UserMenu user={{ userId: "1", name: "John Doe" }} />,
    );

    expect(screen.getByText("JD")).toBeDefined();
  });

  it("opens dropdown on click and shows user info", () => {
    render(
      <UserMenu
        user={{ userId: "1", name: "John Doe", email: "john@test.com" }}
        onLogout={() => {}}
      />,
    );

    fireEvent.click(screen.getByText("JD"));

    expect(screen.getByText("John Doe")).toBeDefined();
    expect(screen.getByText("john@test.com")).toBeDefined();
    expect(screen.getByText("Log out")).toBeDefined();
  });

  it("calls onLogout when logout is clicked", () => {
    const onLogout = vi.fn();
    render(
      <UserMenu
        user={{ userId: "1", name: "Test" }}
        onLogout={onLogout}
      />,
    );

    fireEvent.click(screen.getByText("T"));
    fireEvent.click(screen.getByText("Log out"));

    expect(onLogout).toHaveBeenCalledOnce();
  });
});
