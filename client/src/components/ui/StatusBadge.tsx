import { cn } from "@/src/lib/utils";
import type { ReactNode } from "react";

type Tone = "success" | "warning" | "error" | "neutral" | "brand";

interface StatusBadgeProps {
    tone: Tone;
    children: ReactNode;
    dot?: boolean;
    className?: string;
}

const toneClasses: Record<Tone, string> = {
    success: "bg-emerald-50 text-emerald-700 border-emerald-200",
    warning: "bg-amber-50 text-amber-700 border-amber-200",
    error: "bg-red-50 text-red-700 border-red-200",
    neutral: "bg-slate-100 text-slate-600 border-slate-200",
    brand: "bg-brand-50 text-brand-700 border-brand-200",
};

const dotClasses: Record<Tone, string> = {
    success: "bg-emerald-500",
    warning: "bg-amber-500",
    error: "bg-red-500",
    neutral: "bg-slate-400",
    brand: "bg-brand-500",
};

export function StatusBadge({
    tone,
    children,
    dot = false,
    className = "",
}: StatusBadgeProps) {
    return (
        <span
            className={cn(
                "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium",
                toneClasses[tone],
                className,
            )}
        >
            {dot && (
                <span
                    className={`h-1.5 w-1.5 rounded-full ${dotClasses[tone]}`}
                    aria-hidden="true"
                />
            )}
            {children}
        </span>
    );
}
