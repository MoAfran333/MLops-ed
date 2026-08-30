import {
    Database,
    FileBarChart,
    Lightbulb,
    ShieldCheck,
    Sparkles,
    LayoutDashboard,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

export interface WorkflowStep {
    path: string;
    label: string;
    group: string;
    icon: LucideIcon;
}

export const WORKFLOW_STEPS: WorkflowStep[] = [
    { path: "/dataset", label: "Dataset", group: "Data", icon: Database },
    {
        path: "/profiling",
        label: "Profiling",
        group: "Analysis",
        icon: FileBarChart,
    },
    {
        path: "/recommendation",
        label: "Recommendation",
        group: "Analysis",
        icon: Lightbulb,
    },
    {
        path: "/verification",
        label: "Verification",
        group: "Analysis",
        icon: ShieldCheck,
    },
    {
        path: "/optimization",
        label: "Optimization",
        group: "Analysis",
        icon: Sparkles,
    },
];

export const HOME_STEP: WorkflowStep = {
    path: "/",
    label: "Dashboard",
    group: "Overview",
    icon: LayoutDashboard,
};
