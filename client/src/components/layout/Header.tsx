import { Link } from "react-router-dom";
import { Brain } from "lucide-react";
import { HealthIndicator } from "@/src/components/layout/HealthIndicator";

export function Header({ onMenuClick }: { onMenuClick?: () => void }) {
    return (
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/80 px-4 backdrop-blur-md sm:px-6">
            <div className="flex items-center gap-3">
                {onMenuClick && (
                    <button
                        onClick={onMenuClick}
                        className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden"
                        aria-label="Toggle navigation"
                    >
                        <svg
                            className="h-5 w-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M4 6h16M4 12h16M4 18h16"
                            />
                        </svg>
                    </button>
                )}
                <Link to="/" className="flex items-center gap-2.5">
                    <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 text-white">
                        <Brain className="h-5 w-5" aria-hidden="true" />
                    </span>
                    <div className="leading-tight">
                        <div className="text-base font-bold text-slate-900">
                            ML System
                        </div>
                        <div className="text-xs text-slate-500">
                            Auto-Analysis &amp; Meta-Learning
                        </div>
                    </div>
                </Link>
            </div>
            <HealthIndicator />
        </header>
    );
}
