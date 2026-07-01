import type { ReactNode } from "react";

type BadgeProps = {
  children: ReactNode;
  tone?: "success" | "warning" | "danger" | "neutral";
};

export function Badge({ children, tone = "neutral" }: BadgeProps) {
  return <span className={`badge ${tone}`}>{children}</span>;
}
