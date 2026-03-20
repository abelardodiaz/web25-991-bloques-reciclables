import type { ReactNode } from "react";
import { cn } from "@bloque/ui";

export interface PageContainerProps {
  children: ReactNode;
  maxWidth?: "sm" | "md" | "lg" | "xl" | "2xl" | "full";
  className?: string;
}

const maxWidthClasses: Record<string, string> = {
  sm: "max-w-screen-sm",
  md: "max-w-screen-md",
  lg: "max-w-screen-lg",
  xl: "max-w-screen-xl",
  "2xl": "max-w-screen-2xl",
  full: "max-w-full",
};

export function PageContainer({
  children,
  maxWidth = "xl",
  className,
}: PageContainerProps) {
  return (
    <div
      className={cn(
        "mx-auto w-full px-4 py-6 sm:px-6 lg:px-8",
        maxWidthClasses[maxWidth],
        className,
      )}
    >
      {children}
    </div>
  );
}
