import { ShieldCheck } from "lucide-react";
import { PageHeader } from "@/src/components/ui/PageHeader";
import { VerificationPanel } from "@/src/components/verification/VerificationPanel";

export function Verification() {
    return (
        <div className="space-y-6">
            <PageHeader
                title="Verification"
                description="Compare model performance when trained using 15% of the dataset versus the 85% baseline."
                icon={<ShieldCheck className="h-5 w-5" />}
            />
            <VerificationPanel />
        </div>
    );
}
