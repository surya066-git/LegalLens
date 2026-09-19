import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-surface-900 text-surface-50 hover:bg-surface-900/80",
        secondary:
          "border-transparent bg-surface-100 text-surface-900 hover:bg-surface-100/80",
        outline: "text-surface-900",
        success: "border-transparent bg-success-50 text-success-700 border border-success-200",
        warning: "border-transparent bg-warning-50 text-warning-700 border border-warning-200",
        brand: "border-transparent bg-brand-50 text-brand-700 border border-brand-200",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
