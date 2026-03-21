import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ChatInput } from "../input/chat-input.js";

describe("ChatInput", () => {
  it("renders with default placeholder", () => {
    render(<ChatInput onSend={() => {}} />);
    expect(
      screen.getByPlaceholderText("Escribe un mensaje..."),
    ).toBeDefined();
  });

  it("calls onSend with text when button is clicked", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);
    const input = screen.getByPlaceholderText("Escribe un mensaje...");
    fireEvent.change(input, { target: { value: "Hola mundo" } });
    fireEvent.click(screen.getByText("Enviar"));
    expect(onSend).toHaveBeenCalledWith("Hola mundo");
  });

  it("clears input after sending", () => {
    render(<ChatInput onSend={() => {}} />);
    const input = screen.getByPlaceholderText(
      "Escribe un mensaje...",
    ) as HTMLInputElement;
    fireEvent.change(input, { target: { value: "Test" } });
    fireEvent.click(screen.getByText("Enviar"));
    expect(input.value).toBe("");
  });

  it("does not send empty messages", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);
    fireEvent.click(screen.getByText("Enviar"));
    expect(onSend).not.toHaveBeenCalled();
  });

  it("sends on Enter key press", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);
    const input = screen.getByPlaceholderText("Escribe un mensaje...");
    fireEvent.change(input, { target: { value: "Enter test" } });
    fireEvent.keyDown(input, { key: "Enter" });
    expect(onSend).toHaveBeenCalledWith("Enter test");
  });
});
