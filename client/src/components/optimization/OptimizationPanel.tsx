import { useState } from "react";
import {
    Sparkles,
    Play,
    Download,
    Package,
    Settings2,
    CheckCircle2,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/src/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/src/components/ui/Card";
import { MetricCard } from "@/src/components/ui/MetricCard";
import { LoadingState } from "@/src/components/ui/LoadingState";
import { ErrorState } from "@/src/components/ui/ErrorState";
import { EmptyState } from "@/src/components/ui/EmptyState";
import { ModelSelector } from "@/src/components/ui/ModelSelector";
import { runOptimization, buildDownloadUrl } from "@/src/api/optimization";
import { useWorkflow } from "@/src/context/WorkflowContext";
import type { OptimizationResponse } from "@/src/types/types";

const OPTIMIZATION_MODELS = [
    "RandomForest",
    "DecisionTree",
    "LogisticRegression",
    "LinearRegression",
    "GradientBoosting",
    "AdaBoost",
];

function formatParamValue(val: unknown): string {
    if (val === null || val === undefined) return "—";
    if (typeof val === "object") return JSON.stringify(val);
    if (typeof val === "number") {
        if (Number.isInteger(val)) return String(val);
        return val.toFixed(6);
    }
    return String(val);
}

export function OptimizationPanel() {
    const {
        dataset,
        targetColumn,
        recommendedModel,
        optimizationResult,
        setOptimizationResult,
    } = useWorkflow();
    const [model, setModel] = useState(recommendedModel || "RandomForest");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleOptimize = async () => {
        if (!dataset || !targetColumn) return;
        setLoading(true);
        setError(null);
        try {
            const res = await runOptimization(
                dataset.dataset_id,
                targetColumn,
                model,
            );
            setOptimizationResult(res);
            toast.success("Optimization complete. Final model generated.");
        } catch (err) {
            const message =
                err instanceof Error ? err.message : "Optimization failed.";
            setError(message);
            toast.error(message);
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = () => {
        const result = optimizationResult as OptimizationResponse | null;
        const url = result?.download_url
            ? buildDownloadUrl(result.download_url)
            : buildDownloadUrl("/api/models/best/download");
        window.open(url, "_blank");
    };

    if (!dataset) {
        return (
            <EmptyState
                icon={<Sparkles className="h-10 w-10" />}
                title="No dataset loaded"
                description="Upload a dataset first to optimize and build a model."
            />
        );
    }

    const result = optimizationResult as OptimizationResponse | null;
    const params = result?.best_params ?? null;
    const paramEntries = params ? Object.entries(params) : [];

    return (
        <div className="space-y-4">
            <Card>
                <CardHeader
                    title="Optimize & Build"
                    description="Tune the selected model using 15% of the data, evaluate ensemble variants, and build the final deployment model."
                    icon={<Sparkles className="h-5 w-5" />}
                />
                <CardBody className="space-y-4">
                    <div className="grid gap-4 sm:grid-cols-2">
                        <ModelSelector
                            label="Model"
                            value={model}
                            onChange={setModel}
                            options={OPTIMIZATION_MODELS}
                            disabled={loading}
                        />
                        <div className="flex items-end">
                            <Button
                                onClick={handleOptimize}
                                loading={loading}
                                disabled={!targetColumn || loading}
                                size="lg"
                            >
                                <Play className="h-4 w-4" />
                                Optimize & Build
                            </Button>
                        </div>
                    </div>

                    {loading && (
                        <LoadingState
                            message="Optimizing model and building ensemble variants..."
                            className="py-16"
                        />
                    )}
                    {!loading && error && (
                        <ErrorState
                            message="Optimization failed"
                            detail={error}
                            onRetry={handleOptimize}
                        />
                    )}
                </CardBody>
            </Card>

            {!loading && !error && result && (
                <>
                    <div>
                        <h2 className="mb-3 text-lg font-semibold text-slate-900">
                            Best Configuration
                        </h2>
                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                            <MetricCard
                                label="Model Type"
                                value={result.model_type || "—"}
                                icon={<Package className="h-4 w-4" />}
                                accent="brand"
                            />
                            <MetricCard
                                label="Optimized Variant"
                                value={result.optimized_variant || "—"}
                                icon={<Sparkles className="h-4 w-4" />}
                                accent="brand"
                            />
                            <MetricCard
                                label="Validation Score"
                                value={
                                    result.validation_score !== undefined
                                        ? result.validation_score.toFixed(4)
                                        : "—"
                                }
                                icon={<CheckCircle2 className="h-4 w-4" />}
                                accent="success"
                            />
                        </div>
                    </div>

                    {paramEntries.length > 0 && (
                        <Card>
                            <CardHeader
                                title="Best Parameters"
                                description="Optimal hyperparameters for the final model"
                                icon={<Settings2 className="h-5 w-5" />}
                            />
                            <CardBody>
                                <div className="overflow-hidden rounded-lg border border-slate-200">
                                    <table className="min-w-full divide-y divide-slate-200 text-sm">
                                        <thead className="bg-slate-50">
                                            <tr>
                                                <th className="px-4 py-2.5 text-left font-semibold text-slate-700">
                                                    Parameter
                                                </th>
                                                <th className="px-4 py-2.5 text-left font-semibold text-slate-700">
                                                    Value
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-slate-100">
                                            {paramEntries.map(([key, val]) => (
                                                <tr
                                                    key={key}
                                                    className="hover:bg-slate-50"
                                                >
                                                    <td className="px-4 py-2.5 font-mono text-xs text-slate-600">
                                                        {key}
                                                    </td>
                                                    <td className="px-4 py-2.5 font-mono text-xs text-slate-800">
                                                        {formatParamValue(val)}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </CardBody>
                        </Card>
                    )}

                    <Card className="border-emerald-200 bg-emerald-50/50">
                        <CardBody>
                            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                                <div className="flex items-center gap-3">
                                    <CheckCircle2
                                        className="h-8 w-8 text-emerald-500"
                                        aria-hidden="true"
                                    />
                                    <div>
                                        <p className="text-lg font-semibold text-slate-900">
                                            Final Model Generated
                                        </p>
                                        <p className="text-sm text-slate-500">
                                            {result.model_path ? (
                                                <span className="font-mono text-xs">
                                                    {result.model_path}
                                                </span>
                                            ) : (
                                                "The .pkl model file has been generated."
                                            )}
                                        </p>
                                    </div>
                                </div>
                                <Button
                                    onClick={handleDownload}
                                    size="lg"
                                    variant="secondary"
                                >
                                    <Download className="h-4 w-4" />
                                    Download best_model.pkl
                                </Button>
                            </div>
                        </CardBody>
                    </Card>
                </>
            )}
        </div>
    );
}
