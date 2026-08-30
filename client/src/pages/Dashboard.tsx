import { Link } from "react-router-dom";
import {
    Database,
    FileBarChart,
    Lightbulb,
    ShieldCheck,
    Sparkles,
    Download,
    ArrowRight,
} from "lucide-react";
import { Card, CardBody } from "@/src/components/ui/Card";
import { StatusBadge } from "@/src/components/ui/StatusBadge";
import { HealthIndicator } from "@/src/components/layout/HealthIndicator";
import { useWorkflow } from "@/src/context/WorkflowContext";

const FLOW = [
    {
        label: "Dataset",
        icon: Database,
        path: "/dataset",
        desc: "Upload your CSV file",
    },
    {
        label: "Profile",
        icon: FileBarChart,
        path: "/profiling",
        desc: "Generate a data report",
    },
    {
        label: "Recommend",
        icon: Lightbulb,
        path: "/recommendation",
        desc: "Find the best model",
    },
    {
        label: "Verify",
        icon: ShieldCheck,
        path: "/verification",
        desc: "Test data sensitivity",
    },
    {
        label: "Optimize",
        icon: Sparkles,
        path: "/optimization",
        desc: "Tune & build the model",
    },
    {
        label: "Download",
        icon: Download,
        path: "/optimization",
        desc: "Export the .pkl model",
    },
];

export function Dashboard() {
    const {
        dataset,
        recommendation,
        verificationResult,
        optimizationResult,
        profile,
    } = useWorkflow();

    return (
        <div className="space-y-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-slate-900">
                        ML System
                    </h1>
                    <p className="mt-1 text-sm text-slate-500">
                        Auto-Analysis &amp; Meta-Learning
                    </p>
                </div>
                <HealthIndicator />
            </div>

            {/* Workflow overview */}
            <Card>
                <CardBody>
                    <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">
                        Workflow
                    </h2>
                    <div className="flex flex-wrap items-center gap-2">
                        {FLOW.map((step, i) => {
                            const Icon = step.icon;
                            return (
                                <div
                                    key={i}
                                    className="flex items-center gap-2"
                                >
                                    <Link
                                        to={step.path}
                                        className="group flex flex-col items-center gap-2 rounded-lg border border-slate-200 bg-white p-3 transition-colors hover:border-brand-300 hover:bg-brand-50/50"
                                    >
                                        <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-600 group-hover:bg-brand-100 group-hover:text-brand-600">
                                            <Icon
                                                className="h-5 w-5"
                                                aria-hidden="true"
                                            />
                                        </span>
                                        <div className="text-center">
                                            <p className="text-sm font-medium text-slate-700">
                                                {step.label}
                                            </p>
                                            <p className="text-xs text-slate-400">
                                                {step.desc}
                                            </p>
                                        </div>
                                    </Link>
                                    {i < FLOW.length - 1 && (
                                        <ArrowRight
                                            className="h-4 w-4 shrink-0 text-slate-300"
                                            aria-hidden="true"
                                        />
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </CardBody>
            </Card>

            {/* Current status */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <Card>
                    <CardBody>
                        <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-slate-500">
                                Current Dataset
                            </p>
                            <Database
                                className="h-4 w-4 text-slate-400"
                                aria-hidden="true"
                            />
                        </div>
                        {dataset ? (
                            <div className="mt-2">
                                <p className="text-lg font-semibold text-slate-900">
                                    {dataset.filename}
                                </p>
                                <p className="text-sm text-slate-500">
                                    {dataset.rows} rows · {dataset.columns}{" "}
                                    columns
                                </p>
                            </div>
                        ) : (
                            <div className="mt-2">
                                <p className="text-sm text-slate-400">
                                    No dataset uploaded
                                </p>
                                <Link
                                    to="/dataset"
                                    className="mt-1 inline-flex items-center gap-1 text-sm font-medium text-brand-600 hover:text-brand-700"
                                >
                                    Upload now{" "}
                                    <ArrowRight className="h-3.5 w-3.5" />
                                </Link>
                            </div>
                        )}
                    </CardBody>
                </Card>

                <Card>
                    <CardBody>
                        <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-slate-500">
                                Recommended Model
                            </p>
                            <Lightbulb
                                className="h-4 w-4 text-slate-400"
                                aria-hidden="true"
                            />
                        </div>
                        {recommendation?.recommended_model ? (
                            <div className="mt-2">
                                <p className="text-lg font-semibold text-slate-900">
                                    {recommendation.recommended_model}
                                </p>
                                {recommendation.problem_type && (
                                    <StatusBadge tone="brand" className="mt-1">
                                        {recommendation.problem_type}
                                    </StatusBadge>
                                )}
                            </div>
                        ) : (
                            <p className="mt-2 text-sm text-slate-400">
                                No recommendation yet
                            </p>
                        )}
                    </CardBody>
                </Card>

                <Card>
                    <CardBody>
                        <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-slate-500">
                                Final Model
                            </p>
                            <Sparkles
                                className="h-4 w-4 text-slate-400"
                                aria-hidden="true"
                            />
                        </div>
                        {optimizationResult ? (
                            <div className="mt-2">
                                <p className="text-lg font-semibold text-slate-900">
                                    {optimizationResult.optimized_variant ||
                                        optimizationResult.model_type ||
                                        "Built"}
                                </p>
                                <Link
                                    to="/optimization"
                                    className="mt-1 inline-flex items-center gap-1 text-sm font-medium text-brand-600 hover:text-brand-700"
                                >
                                    Download model{" "}
                                    <ArrowRight className="h-3.5 w-3.5" />
                                </Link>
                            </div>
                        ) : (
                            <p className="mt-2 text-sm text-slate-400">
                                Not optimized yet
                            </p>
                        )}
                    </CardBody>
                </Card>
            </div>

            {/* Quick stats */}
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                {[
                    { label: "Profile", done: !!profile, path: "/profiling" },
                    {
                        label: "Recommendation",
                        done: !!recommendation,
                        path: "/recommendation",
                    },
                    {
                        label: "Verification",
                        done: !!verificationResult,
                        path: "/verification",
                    },
                    {
                        label: "Optimization",
                        done: !!optimizationResult,
                        path: "/optimization",
                    },
                ].map((s) => (
                    <Link key={s.label} to={s.path}>
                        <Card className="h-full transition-colors hover:border-brand-300">
                            <CardBody className="flex items-center justify-between">
                                <span className="text-sm font-medium text-slate-600">
                                    {s.label}
                                </span>
                                <StatusBadge
                                    tone={s.done ? "success" : "neutral"}
                                    dot
                                >
                                    {s.done ? "Done" : "Pending"}
                                </StatusBadge>
                            </CardBody>
                        </Card>
                    </Link>
                ))}
            </div>
        </div>
    );
}
