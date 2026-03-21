export interface Message {
  id: string;
  text: string;
  timestamp: Date;
  direction: "sent" | "received";
  status?: "sending" | "sent" | "delivered" | "read";
}
