import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { NavItem } from "../navigation/nav-item.js";

describe("NavItem", () => {
  it("renders as anchor when href is provided", () => {
    render(<NavItem label="Users" href="/users" />);

    const link = screen.getByText("Users").closest("a");
    expect(link).toBeDefined();
    expect(link?.getAttribute("href")).toBe("/users");
  });

  it("renders as button when onClick is provided", () => {
    const onClick = vi.fn();
    render(<NavItem label="Action" onClick={onClick} />);

    const button = screen.getByText("Action").closest("button");
    expect(button).toBeDefined();

    fireEvent.click(button!);
    expect(onClick).toHaveBeenCalledOnce();
  });

  it("shows badge when provided", () => {
    render(<NavItem label="Inbox" href="/inbox" badge={5} />);

    expect(screen.getByText("5")).toBeDefined();
  });

  it("hides label and badge when collapsed", () => {
    render(<NavItem label="Users" href="/users" badge={3} collapsed />);

    expect(screen.queryByText("Users")).toBeNull();
    expect(screen.queryByText("3")).toBeNull();
  });

  it("sets aria-current=page when active", () => {
    render(<NavItem label="Home" href="/" active />);

    const link = screen.getByText("Home").closest("a");
    expect(link?.getAttribute("aria-current")).toBe("page");
  });
});
