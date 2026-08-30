import type { ReactNode } from "react";

interface MetricCardProps {
    label: string;
    value: ReactNode;
    hint?: string;
    icon?: ReactNode;
    accent?: "default" | "success" | "warning" | "error" | "brand";
}

const accentClasses = {
    default: "text-slate-900",
    success: "text-emerald-600",
    warning: "text-amber-600",
    error: "text-red-600",
    brand: "text-brand-600",
};

const iconBgClasses = {
    default: "bg-slate-100 text-slate-600",
    success: "bg-emerald-50 text-emerald-600",
    warning: "bg-amber-50 text-amber-600",
    error: "bg-red-50 text-red-600",
    brand: "bg-brand-50 text-brand-600",
};

export function MetricCard({
    label,
    value,
    hint,
    icon,
    accent = "default",
}: MetricCardProps) {
    return (
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-500">
                    {label}
                </span>
                {icon && (
                    <span
                        className={`flex h-8 w-8 items-center justify-center rounded-lg ${iconBgClasses[accent]}`}
                    >
                        {icon}
                    </span>
                )}
            </div>
            <div className={`mt-2 text-2xl font-bold ${accentClasses[accent]}`}>
                {value}
            </div>
            {hint && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
        </div>
    );
}
