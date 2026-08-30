import { Lightbulb } from "lucide-react";
import { PageHeader } from "@/src/components/ui/PageHeader";
import { RecommendationPanel } from "@/src/components/recommendation/RecommendationPanel";

export function Recommendation() {
    return (
        <div className="space-y-6">
            <PageHeader
                title="Recommendation"
                description="The meta-learner analyzes your dataset's meta-features and recommends the most suitable model."
                icon={<Lightbulb className="h-5 w-5" />}
            />
            <RecommendationPanel />
        </div>
    );
}
