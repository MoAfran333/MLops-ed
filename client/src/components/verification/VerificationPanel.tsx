import { useState } from "react";
import {
    ShieldCheck,
    Play,
    TrendingDown,
    TrendingUp,
    CheckCircle2,
    AlertTriangle,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/src/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/src/components/ui/Card";
import { MetricCard } from "@/src/components/ui/MetricCard";
import { StatusBadge } from "@/src/components/ui/StatusBadge";
import { LoadingState } from "@/src/components/ui/LoadingState";
import { ErrorState } from "@/src/components/ui/ErrorState";
import { EmptyState } from "@/src/components/ui/EmptyState";
import { ModelSelector } from "@/src/components/ui/ModelSelector";
import { runVerification } from "@/src/api/verification";
import { useWorkflow } from "@/src/context/WorkflowContext";
import type { VerificationResponse } from "@/src/types/types";

const VERIFICATION_MODELS = [
    "LogisticRegression",
    "RandomForest",
    "LinearRegression",
    "DecisionTree",
    "GaussianNB",
];

export function VerificationPanel() {
    const {
        dataset,
        targetColumn,
        recommendedModel,
        verificationResult,
        setVerificationResult,
    } = useWorkflow();
    const [model, setModel] = useState(recommendedModel || "RandomForest");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleRun = async () => {
        if (!dataset || !targetColumn) return;
        setLoading(true);
        setError(null);
        try {
            const res = await runVerification(
                dataset.dataset_id,
                targetColumn,
                model,
            );
            setVerificationResult(res);
            toast.success("Verification completed.");
        } catch (err) {
            const message =
                err instanceof Error ? err.message : "Verification failed.";
            setError(message);
            toast.error(message);
        } finally {
            setLoading(false);
        }
    };

    if (!dataset) {
        return (
            <EmptyState
                icon={<ShieldCheck className="h-10 w-10" />}
                title="No dataset loaded"
                description="Upload a dataset first to run verification."
            />
        );
    }

    const result = verificationResult as VerificationResponse | null;
    const dropPercent = result?.drop_percent;
    const isSensitive = dropPercent !== undefined && dropPercent > 5;

    return (
        <div className="space-y-4">
            <Card>
                <CardHeader
                    title="15% vs 85% Verification"
                    description="Compare model performance when trained using 15% of the dataset versus the 85% baseline."
                    icon={<ShieldCheck className="h-5 w-5" />}
                />
                <CardBody className="space-y-4">
                    <div className="grid gap-4 sm:grid-cols-2">
                        <ModelSelector
                            label="Model"
                            value={model}
                            onChange={setModel}
                            options={VERIFICATION_MODELS}
                            disabled={loading}
                        />
                        <div className="flex items-end">
                            <Button
                                onClick={handleRun}
                                loading={loading}
                                disabled={!targetColumn || loading}
                                size="lg"
                            >
                                <Play className="h-4 w-4" />
                                Run Verification
                            </Button>
                        </div>
                    </div>

                    {loading && (
                        <LoadingState message="Running verification..." />
                    )}
                    {!loading && error && (
                        <ErrorState
                            message="Verification failed"
                            detail={error}
                            onRetry={handleRun}
                        />
                    )}
                </CardBody>
            </Card>

            {!loading && !error && result && (
                <>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                        <MetricCard
                            label="Baseline Score"
                            value={
                                result.baseline_score !== undefined
                                    ? result.baseline_score.toFixed(4)
                                    : "—"
                            }
                            hint="85% training data"
                            icon={<TrendingUp className="h-4 w-4" />}
                            accent="success"
                        />
                        <MetricCard
                            label="Small Train Score"
                            value={
                                result.small_train_score !== undefined
                                    ? result.small_train_score.toFixed(4)
                                    : "—"
                            }
                            hint="15% training data"
                            icon={<TrendingDown className="h-4 w-4" />}
                            accent="warning"
                        />
                        <MetricCard
                            label="Performance Drop"
                            value={
                                dropPercent !== undefined
                                    ? `${dropPercent.toFixed(2)}%`
                                    : "—"
                            }
                            hint={
                                result.score_drop !== undefined
                                    ? `Score drop: ${result.score_drop.toFixed(4)}`
                                    : undefined
                            }
                            icon={<TrendingDown className="h-4 w-4" />}
                            accent={isSensitive ? "error" : "success"}
                        />
                    </div>

                    <Card
                        className={
                            isSensitive
                                ? "border-amber-200 bg-amber-50/50"
                                : "border-emerald-200 bg-emerald-50/50"
                        }
                    >
                        <CardBody>
                            <div className="flex items-center gap-3">
                                {isSensitive ? (
                                    <AlertTriangle
                                        className="h-8 w-8 text-amber-500"
                                        aria-hidden="true"
                                    />
                                ) : (
                                    <CheckCircle2
                                        className="h-8 w-8 text-emerald-500"
                                        aria-hidden="true"
                                    />
                                )}
                                <div>
                                    <p className="text-lg font-semibold text-slate-900">
                                        {isSensitive
                                            ? "Sensitive to data reduction"
                                            : "Robust to data reduction"}
                                    </p>
                                    <p className="text-sm text-slate-500">
                                        {isSensitive
                                            ? "This model's performance degrades significantly with less training data."
                                            : "This model maintains stable performance even with reduced training data."}
                                    </p>
                                </div>
                                <div className="ml-auto">
                                    <StatusBadge
                                        tone={
                                            isSensitive ? "warning" : "success"
                                        }
                                    >
                                        {isSensitive ? "Sensitive" : "Robust"}
                                    </StatusBadge>
                                </div>
                            </div>
                        </CardBody>
                    </Card>
                </>
            )}
        </div>
    );
}
