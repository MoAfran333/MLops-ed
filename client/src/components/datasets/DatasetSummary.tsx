import { FileText, Hash, Columns3, Target, Type } from "lucide-react";
import { MetricCard } from "@/src/components/ui/MetricCard";
import { StatusBadge } from "@/src/components/ui/StatusBadge";
import type { DatasetInfo } from "@/src/types/types";

interface DatasetSummaryProps {
    dataset: DatasetInfo;
    targetColumn?: string;
    problemType?: string;
}

export function DatasetSummary({
    dataset,
    targetColumn,
    problemType,
}: DatasetSummaryProps) {
    return (
        <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-3">
                <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
                    <FileText
                        className="h-4 w-4 text-brand-500"
                        aria-hidden="true"
                    />
                    {dataset.filename}
                </div>
                {problemType && (
                    <StatusBadge tone="brand">
                        {problemType.charAt(0).toUpperCase() +
                            problemType.slice(1)}
                    </StatusBadge>
                )}
            </div>

            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <MetricCard
                    label="Rows"
                    value={dataset.rows.toLocaleString()}
                    icon={<Hash className="h-4 w-4" />}
                />
                <MetricCard
                    label="Columns"
                    value={dataset.columns}
                    icon={<Columns3 className="h-4 w-4" />}
                />
                <MetricCard
                    label="Target"
                    value={targetColumn || "—"}
                    icon={<Target className="h-4 w-4" />}
                    accent={targetColumn ? "brand" : "default"}
                />
                <MetricCard
                    label="Problem Type"
                    value={
                        problemType
                            ? problemType.charAt(0).toUpperCase() +
                              problemType.slice(1)
                            : "—"
                    }
                    icon={<Type className="h-4 w-4" />}
                    accent={problemType ? "brand" : "default"}
                />
            </div>
        </div>
    );
}
