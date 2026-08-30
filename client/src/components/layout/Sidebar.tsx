import { NavLink } from "react-router-dom";
import { Brain } from "lucide-react";
import { WorkflowStepper } from "@/src/components/layout/WorkflowStepper";

export function Sidebar() {
    return (
        <aside className="flex h-full w-64 flex-col border-r border-slate-200 bg-white">
            <div className="flex h-16 items-center gap-2.5 border-b border-slate-200 px-5">
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
            </div>

            <div className="flex-1 overflow-y-auto p-4">
                <nav className="mb-6" aria-label="Main navigation">
                    <NavLink
                        to="/"
                        end
                        className={({ isActive }) =>
                            `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                                isActive
                                    ? "bg-brand-50 text-brand-700"
                                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                            }`
                        }
                    >
                        <span className="flex h-5 w-5 items-center justify-center">
                            <span
                                className="h-2 w-2 rounded-full bg-slate-300"
                                aria-hidden="true"
                            />
                        </span>
                        Dashboard
                    </NavLink>
                </nav>

                <WorkflowStepper />
            </div>

            <div className="border-t border-slate-200 p-4">
                <p className="text-xs text-slate-400">
                    Frontend client for FastAPI ML backend
                </p>
            </div>
        </aside>
    );
}
