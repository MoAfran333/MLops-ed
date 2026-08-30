import { Loader2 } from "lucide-react";

interface LoadingStateProps {
    message?: string;
    className?: string;
}

export function LoadingState({
    message = "Loading...",
    className = "",
}: LoadingStateProps) {
    return (
        <div
            className={`flex flex-col items-center justify-center gap-3 py-12 ${className}`}
        >
            <Loader2
                className="h-8 w-8 animate-spin text-brand-500"
                aria-hidden="true"
            />
            <p className="text-sm font-medium text-slate-600">{message}</p>
        </div>
    );
}

export function Spinner({ className = "" }: { className?: string }) {
    return (
        <Loader2
            className={`h-5 w-5 animate-spin ${className}`}
            aria-hidden="true"
        />
    );
}
