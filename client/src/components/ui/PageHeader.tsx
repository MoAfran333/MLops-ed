import type { ReactNode } from "react";

interface PageHeaderProps {
    title: string;
    description?: string;
    icon?: ReactNode;
    action?: ReactNode;
}

export function PageHeader({
    title,
    description,
    icon,
    action,
}: PageHeaderProps) {
    return (
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-3">
                {icon && (
                    <div className="mt-0.5 flex h-10 w-10 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
                        {icon}
                    </div>
                )}
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-slate-900">
                        {title}
                    </h1>
                    {description && (
                        <p className="mt-1 max-w-2xl text-sm text-slate-500">
                            {description}
                        </p>
                    )}
                </div>
            </div>
            {action}
        </div>
    );
}
