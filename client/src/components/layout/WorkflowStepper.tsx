import { NavLink } from "react-router-dom";
import { Check, Circle, CircleDot } from "lucide-react";
import { WORKFLOW_STEPS } from "@/src/components/layout/workflowSteps";
import { useWorkflow } from "@/src/context/WorkflowContext";
import type { LucideIcon } from "lucide-react";

type StepStatus = "completed" | "current" | "todo";

function getStepStatus(
    stepPath: string,
    hasDataset: boolean,
    hasProfile: boolean,
    hasRecommendation: boolean,
    hasVerification: boolean,
    hasOptimization: boolean,
): StepStatus {
    if (stepPath === "/dataset") {
        return hasDataset ? "completed" : "todo";
    }
    if (stepPath === "/profiling") {
        return hasProfile ? "completed" : hasDataset ? "todo" : "todo";
    }
    if (stepPath === "/recommendation") {
        return hasRecommendation ? "completed" : "todo";
    }
    if (stepPath === "/verification") {
        return hasVerification ? "completed" : "todo";
    }
    if (stepPath === "/optimization") {
        return hasOptimization ? "completed" : "todo";
    }
    return "todo";
}

function StepRow({
    to,
    label,
    icon: Icon,
    status,
}: {
    to: string;
    label: string;
    icon: LucideIcon;
    status: StepStatus;
}) {
    return (
        <NavLink
            to={to}
            className={({ isActive }) =>
                `group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    isActive
                        ? "bg-brand-50 text-brand-700"
                        : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`
            }
        >
            <span className="flex h-5 w-5 shrink-0 items-center justify-center">
                {status === "completed" ? (
                    <Check
                        className="h-4 w-4 text-emerald-500"
                        aria-label="Completed"
                    />
                ) : status === "current" ? (
                    <CircleDot
                        className="h-4 w-4 text-brand-500"
                        aria-label="Current"
                    />
                ) : (
                    <Circle
                        className="h-4 w-4 text-slate-300"
                        aria-label="Not started"
                    />
                )}
            </span>
            <Icon className="h-4 w-4 shrink-0 opacity-70" aria-hidden="true" />
            <span>{label}</span>
        </NavLink>
    );
}

export function WorkflowStepper() {
    const {
        dataset,
        profile,
        recommendation,
        verificationResult,
        optimizationResult,
    } = useWorkflow();

    const hasDataset = !!dataset;
    const hasProfile = !!profile;
    const hasRecommendation = !!recommendation;
    const hasVerification = !!verificationResult;
    const hasOptimization = !!optimizationResult;

    const groups = WORKFLOW_STEPS.reduce<Record<string, typeof WORKFLOW_STEPS>>(
        (acc, step) => {
            (acc[step.group] ||= []).push(step);
            return acc;
        },
        {},
    );

    return (
        <nav className="space-y-5" aria-label="Workflow steps">
            {Object.entries(groups).map(([group, steps]) => (
                <div key={group}>
                    <p className="mb-1.5 px-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
                        {group}
                    </p>
                    <div className="space-y-0.5">
                        {steps.map((step) => (
                            <StepRow
                                key={step.path}
                                to={step.path}
                                label={step.label}
                                icon={step.icon}
                                status={getStepStatus(
                                    step.path,
                                    hasDataset,
                                    hasProfile,
                                    hasRecommendation,
                                    hasVerification,
                                    hasOptimization,
                                )}
                            />
                        ))}
                    </div>
                </div>
            ))}
        </nav>
    );
}
