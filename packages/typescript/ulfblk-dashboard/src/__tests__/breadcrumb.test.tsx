import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Breadcrumb } from "../navigation/breadcrumb.js";

describe("Breadcrumb", () => {
  it("renders nothing for empty items", () => {
    const { container } = render(<Breadcrumb items={[]} />);

    expect(container.innerHTML).toBe("");
  });

  it("renders breadcrumb trail with links", () => {
    render(
      <Breadcrumb
        items={[
          { label: "Home", href: "/" },
          { label: "Users", href: "/users" },
          { label: "John" },
        ]}
      />,
    );

    const homeLink = screen.getByText("Home").closest("a");
    expect(homeLink?.getAttribute("href")).toBe("/");

    const usersLink = screen.getByText("Users").closest("a");
    expect(usersLink?.getAttribute("href")).toBe("/users");

    // Last item is not a link
    const john = screen.getByText("John");
    expect(john.closest("a")).toBeNull();
    expect(john.getAttribute("aria-current")).toBe("page");
  });

  it("renders with aria-label for navigation", () => {
    render(
      <Breadcrumb items={[{ label: "Home" }]} />,
    );

    expect(screen.getByLabelText("Breadcrumb")).toBeDefined();
  });
});
