import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MessageBubble } from "../chat/message-bubble.js";
import { MessageList } from "../chat/message-list.js";
import type { Message } from "../types.js";

const sentMessage: Message = {
  id: "1",
  text: "Hola, como estas?",
  timestamp: new Date(2026, 0, 15, 10, 30),
  direction: "sent",
  status: "delivered",
};

const receivedMessage: Message = {
  id: "2",
  text: "Bien, gracias!",
  timestamp: new Date(2026, 0, 15, 10, 31),
  direction: "received",
};

describe("MessageBubble", () => {
  it("renders sent message text", () => {
    render(<MessageBubble message={sentMessage} />);
    expect(screen.getByText("Hola, como estas?")).toBeDefined();
  });

  it("renders received message text", () => {
    render(<MessageBubble message={receivedMessage} />);
    expect(screen.getByText("Bien, gracias!")).toBeDefined();
  });

  it("renders timestamp", () => {
    render(<MessageBubble message={sentMessage} />);
    expect(screen.getByText("10:30")).toBeDefined();
  });

  it("renders status indicator for sent messages", () => {
    render(<MessageBubble message={sentMessage} />);
    expect(screen.getByText("vv")).toBeDefined();
  });
});

describe("MessageList", () => {
  it("renders empty label when no messages", () => {
    render(<MessageList messages={[]} />);
    expect(screen.getByText("No hay mensajes")).toBeDefined();
  });

  it("renders all messages", () => {
    render(<MessageList messages={[sentMessage, receivedMessage]} />);
    expect(screen.getByText("Hola, como estas?")).toBeDefined();
    expect(screen.getByText("Bien, gracias!")).toBeDefined();
  });
});
