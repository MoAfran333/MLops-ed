import { useState } from "react";
import { Lightbulb, Sparkles, Target } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/src/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/src/components/ui/Card";
import { MetricCard } from "@/src/components/ui/MetricCard";
import { StatusBadge } from "@/src/components/ui/StatusBadge";
import { LoadingState } from "@/src/components/ui/LoadingState";
import { ErrorState } from "@/src/components/ui/ErrorState";
import { EmptyState } from "@/src/components/ui/EmptyState";
import { TargetColumnSelector } from "@/src/components/ui/TargetColumnSelector";
import { getRecommendation } from "@/src/api/recommendation";
import { useWorkflow } from "@/src/context/WorkflowContext";
import type { MetaFeatures } from "@/src/types/types";

const META_LABELS: { key: string; label: string }[] = [
    { key: "n_samples", label: "Samples" },
    { key: "n_features", label: "Features" },
    { key: "missing_ratio", label: "Missing Ratio" },
    { key: "avg_variance", label: "Average Variance" },
    { key: "avg_abs_correlation", label: "Avg Absolute Correlation" },
    { key: "class_entropy", label: "Class Entropy" },
    { key: "imbalance_ratio", label: "Imbalance Ratio" },
];

function formatValue(val: unknown): string {
    if (val === null || val === undefined) return "—";
    if (typeof val === "number") {
        if (Number.isInteger(val)) return val.toLocaleString();
        return val.toFixed(4);
    }
    return String(val);
}

export function RecommendationPanel() {
    const {
        dataset,
        targetColumn,
        setTargetColumn,
        recommendation,
        setRecommendation,
        setProblemType,
        setMetaFeatures,
        setRecommendedModel,
    } = useWorkflow();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleRecommend = async () => {
        if (!dataset || !targetColumn) return;
        setLoading(true);
        setError(null);
        try {
            const res = await getRecommendation(
                dataset.dataset_id,
                targetColumn,
            );
            setRecommendation(res);
            if (res.problem_type) setProblemType(res.problem_type);
            if (res.meta_features)
                setMetaFeatures(res.meta_features as MetaFeatures);
            if (res.recommended_model)
                setRecommendedModel(res.recommended_model);
            toast.success("Recommendation generated successfully.");
        } catch (err) {
            const message =
                err instanceof Error
                    ? err.message
                    : "Failed to generate recommendation.";
            setError(message);
            toast.error(message);
        } finally {
            setLoading(false);
        }
    };

    if (!dataset) {
        return (
            <EmptyState
                icon={<Lightbulb className="h-10 w-10" />}
                title="No dataset loaded"
                description="Upload a dataset first to get a model recommendation."
            />
        );
    }

    const meta = recommendation?.meta_features ?? null;
    const problemType = recommendation?.problem_type || "";
    const recommendedModel = recommendation?.recommended_model || "";

    return (
        <div className="space-y-4">
            <Card>
                <CardHeader
                    title="Model Recommendation"
                    description="Select a target column and let the meta-learner recommend the best model."
                    icon={<Lightbulb className="h-5 w-5" />}
                />
                <CardBody className="space-y-4">
                    <div className="max-w-xs">
                        <TargetColumnSelector
                            value={targetColumn}
                            onChange={setTargetColumn}
                            columns={dataset.column_names ?? []}
                            disabled={loading}
                        />
                    </div>
                    <div className="flex items-center gap-3">
                        <Button
                            onClick={handleRecommend}
                            loading={loading}
                            disabled={!targetColumn || loading}
                        >
                            <Sparkles className="h-4 w-4" />
                            {recommendation
                                ? "Re-run Recommendation"
                                : "Get Recommendation"}
                        </Button>
                        {targetColumn && (
                            <span className="flex items-center gap-1.5 text-sm text-slate-500">
                                <Target className="h-4 w-4" />
                                Target:{" "}
                                <span className="font-medium text-slate-700">
                                    {targetColumn}
                                </span>
                            </span>
                        )}
                    </div>

                    {loading && (
                        <LoadingState message="Computing meta-features and predicting best model..." />
                    )}
                    {!loading && error && (
                        <ErrorState
                            message="Recommendation failed"
                            detail={error}
                            onRetry={handleRecommend}
                        />
                    )}
                </CardBody>
            </Card>

            {!loading && !error && recommendation && (
                <>
                    <Card className="border-brand-200 bg-linear-to-br from-brand-50/50 to-white">
                        <CardBody>
                            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                                <div>
                                    <p className="text-sm font-medium text-slate-500">
                                        Recommended Model
                                    </p>
                                    <p className="mt-1 text-3xl font-bold text-slate-900">
                                        {recommendedModel || "—"}
                                    </p>
                                    {problemType && (
                                        <StatusBadge
                                            tone="brand"
                                            className="mt-2"
                                        >
                                            {problemType
                                                .charAt(0)
                                                .toUpperCase() +
                                                problemType.slice(1)}
                                        </StatusBadge>
                                    )}
                                </div>
                                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-100">
                                    <Sparkles
                                        className="h-8 w-8 text-brand-600"
                                        aria-hidden="true"
                                    />
                                </div>
                            </div>
                        </CardBody>
                    </Card>

                    {meta && (
                        <Card>
                            <CardHeader
                                title="Meta-Features"
                                description="Computed characteristics of your dataset"
                                icon={<Lightbulb className="h-5 w-5" />}
                            />
                            <CardBody>
                                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                                    {META_LABELS.map(({ key, label }) => (
                                        <MetricCard
                                            key={key}
                                            label={label}
                                            value={formatValue(meta[key])}
                                        />
                                    ))}
                                </div>
                            </CardBody>
                        </Card>
                    )}
                </>
            )}
        </div>
    );
}
