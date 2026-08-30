import type { HTMLAttributes, ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
    children: ReactNode;
}

export function Card({ className = "", children, ...props }: CardProps) {
    return (
        <div
            className={`rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}
            {...props}
        >
            {children}
        </div>
    );
}

interface CardHeaderProps {
    title: string;
    description?: string;
    icon?: ReactNode;
    action?: ReactNode;
    className?: string;
}

export function CardHeader({
    title,
    description,
    icon,
    action,
    className = "",
}: CardHeaderProps) {
    return (
        <div
            className={`flex items-start justify-between gap-4 border-b border-slate-100 p-5 ${className}`}
        >
            <div className="flex items-start gap-3">
                {icon && <div className="mt-0.5 text-brand-600">{icon}</div>}
                <div>
                    <h3 className="text-base font-semibold text-slate-900">
                        {title}
                    </h3>
                    {description && (
                        <p className="mt-0.5 text-sm text-slate-500">
                            {description}
                        </p>
                    )}
                </div>
            </div>
            {action}
        </div>
    );
}

export function CardBody({
    className = "",
    children,
}: {
    className?: string;
    children: ReactNode;
}) {
    return <div className={`p-5 ${className}`}>{children}</div>;
}
