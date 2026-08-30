import { FileBarChart } from "lucide-react";
import { PageHeader } from "@/src/components/ui/PageHeader";
import { ProfilingPanel } from "@/src/components/profiling/ProfilingPanel";

export function Profiling() {
    return (
        <div className="space-y-6">
            <PageHeader
                title="Profiling"
                description="Generate a comprehensive statistical profile of your dataset, including distributions, correlations, and missing value analysis."
                icon={<FileBarChart className="h-5 w-5" />}
            />
            <ProfilingPanel />
        </div>
    );
}
