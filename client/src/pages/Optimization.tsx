import { Sparkles } from "lucide-react";
import { PageHeader } from "@/src/components/ui/PageHeader";
import { OptimizationPanel } from "@/src/components/optimization/OptimizationPanel";

export function Optimization() {
    return (
        <div className="space-y-6">
            <PageHeader
                title="Optimization"
                description="Tune the selected model using 15% of the data, evaluate ensemble variants, and build the final deployment model."
                icon={<Sparkles className="h-5 w-5" />}
            />
            <OptimizationPanel />
        </div>
    );
}
