import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { DashboardLayout } from "../layout/dashboard-layout.js";
import { Sidebar } from "../layout/sidebar.js";
import { Header } from "../layout/header.js";

describe("DashboardLayout", () => {
  it("renders sidebar, header, and content", () => {
    render(
      <DashboardLayout
        sidebar={<Sidebar><nav>sidebar-nav</nav></Sidebar>}
        header={<Header />}
      >
        <div>main-content</div>
      </DashboardLayout>,
    );

    expect(screen.getByText("sidebar-nav")).toBeDefined();
    expect(screen.getByText("main-content")).toBeDefined();
  });

  it("renders without header", () => {
    render(
      <DashboardLayout sidebar={<Sidebar><span>nav</span></Sidebar>}>
        <div>content-only</div>
      </DashboardLayout>,
    );

    expect(screen.getByText("content-only")).toBeDefined();
  });

  it("applies custom className", () => {
    const { container } = render(
      <DashboardLayout
        sidebar={<Sidebar><span>s</span></Sidebar>}
        className="custom-layout"
      >
        <div>c</div>
      </DashboardLayout>,
    );

    const layout = container.firstChild as HTMLElement;
    expect(layout.className).toContain("custom-layout");
  });

  it("passes defaultCollapsed to provider", () => {
    render(
      <DashboardLayout
        defaultCollapsed={true}
        sidebar={<Sidebar><span>s</span></Sidebar>}
      >
        <div>c</div>
      </DashboardLayout>,
    );

    const sidebar = document.querySelector("aside");
    expect(sidebar?.style.width).toBe("4rem");
  });

  it("renders children inside main element", () => {
    render(
      <DashboardLayout sidebar={<Sidebar><span>s</span></Sidebar>}>
        <p>inside-main</p>
      </DashboardLayout>,
    );

    const main = document.querySelector("main");
    expect(main).toBeDefined();
    expect(main?.textContent).toContain("inside-main");
  });
});
