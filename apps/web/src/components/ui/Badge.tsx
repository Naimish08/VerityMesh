import * as React from "react"
import { cn } from "@/lib/utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "verified" | "refuted" | "inconclusive" | "info" | "outline"
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        {
          "border-transparent bg-primary/20 text-primary": variant === "default" || variant === "info",
          "border-transparent bg-[#10b981]/20 text-[#10b981]": variant === "verified",
          "border-transparent bg-[#ef4444]/20 text-[#ef4444]": variant === "refuted",
          "border-transparent bg-[#f59e0b]/20 text-[#f59e0b]": variant === "inconclusive",
          "text-foreground": variant === "outline",
        },
        className
      )}
      {...props}
    />
  )
}

export { Badge }
