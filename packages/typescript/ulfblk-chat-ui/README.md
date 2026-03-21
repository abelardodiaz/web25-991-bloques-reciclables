# @ulfblk/chat-ui

React chat components - message bubbles, chat input, typing indicator, connection status. Zero external dependencies (only React + Tailwind CSS variables).

## Install

```bash
pnpm add @ulfblk/chat-ui
```

## Quick Start

```tsx
import {
  ChatContainer,
  MessageList,
  ChatInput,
  TypingIndicator,
  ConnectionStatus,
  useChat,
} from "@ulfblk/chat-ui";
import type { Message } from "@ulfblk/chat-ui";

function Chat() {
  const { messages, addMessage } = useChat();

  const handleSend = (text: string) => {
    addMessage({
      id: crypto.randomUUID(),
      text,
      timestamp: new Date(),
      direction: "sent",
      status: "sending",
    });
  };

  return (
    <div className="flex h-screen flex-col">
      <ConnectionStatus online={true} />
      <ChatContainer>
        <MessageList messages={messages} />
        <TypingIndicator />
      </ChatContainer>
      <ChatInput onSend={handleSend} />
    </div>
  );
}
```

## Components

| Component | Description |
|-----------|-------------|
| `MessageBubble` | Single message bubble (sent/received styling) |
| `MessageList` | List of MessageBubble components with empty state |
| `ChatContainer` | Scrollable wrapper with auto-scroll to bottom |
| `ChatInput` | Text input + send button, Enter to submit |
| `TypingIndicator` | Three-dot animation with label |
| `ConnectionStatus` | Online/offline indicator with dot |

## Hooks

| Hook | Description |
|------|-------------|
| `useChat(initialMessages?)` | Message state: messages, addMessage, clearMessages |

## i18n

All text labels are configurable via props with Spanish defaults:

- `emptyLabel` - "No hay mensajes"
- `placeholder` - "Escribe un mensaje..."
- `sendLabel` - "Enviar"
- `label` (TypingIndicator) - "Escribiendo..."
- `onlineLabel` - "Conectado"
- `offlineLabel` - "Desconectado"
