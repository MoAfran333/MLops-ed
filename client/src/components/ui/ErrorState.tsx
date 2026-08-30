import { AlertCircle } from "lucide-react";

interface ErrorStateProps {
    message: string;
    detail?: string;
    onRetry?: () => void;
    className?: string;
}

export function ErrorState({
    message,
    detail,
    onRetry,
    className = "",
}: ErrorStateProps) {
    return (
        <div
            className={`flex flex-col items-center justify-center gap-3 rounded-lg border border-red-200 bg-red-50 p-6 text-center ${className}`}
            role="alert"
        >
            <AlertCircle className="h-8 w-8 text-red-500" aria-hidden="true" />
            <div>
                <p className="font-medium text-red-900">{message}</p>
                {detail && (
                    <p className="mt-1 text-sm text-red-600">{detail}</p>
                )}
            </div>
            {onRetry && (
                <button
                    onClick={onRetry}
                    className="mt-1 rounded-lg border border-red-300 bg-white px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100"
                >
                    Try again
                </button>
            )}
        </div>
    );
}
