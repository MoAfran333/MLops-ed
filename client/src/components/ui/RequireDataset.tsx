import { useNavigate } from "react-router-dom";
import { Database, ArrowRight } from "lucide-react";
import { Button } from "@/src/components/ui/Button";
import { EmptyState } from "@/src/components/ui/EmptyState";

interface RequireDatasetProps {
    title: string;
    description: string;
}

export function RequireDataset({ title, description }: RequireDatasetProps) {
    const navigate = useNavigate();
    return (
        <EmptyState
            icon={<Database className="h-10 w-10" />}
            title={title}
            description={description}
            action={
                <Button onClick={() => navigate("/dataset")} className="mt-2">
                    Go to Dataset
                    <ArrowRight className="h-4 w-4" />
                </Button>
            }
        />
    );
}
