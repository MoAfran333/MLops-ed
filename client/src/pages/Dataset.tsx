import { Database } from "lucide-react";
import { PageHeader } from "@/src/components/ui/PageHeader";
import { Card, CardBody, CardHeader } from "@/src/components/ui/Card";
import { DatasetUpload } from "@/src/components/datasets/DatasetUpload";
import { DatasetSummary } from "@/src/components/datasets/DatasetSummary";
import { DatasetPreview } from "@/src/components/datasets/DatasetPreview";
import { TargetColumnSelector } from "@/src/components/ui/TargetColumnSelector";
import { useWorkflow } from "@/src/context/WorkflowContext";

export function Dataset() {
    const { dataset, targetColumn, setTargetColumn, problemType } =
        useWorkflow();

    return (
        <div className="space-y-6">
            <PageHeader
                title="Dataset"
                description="Upload a CSV file to begin the ML workflow. The backend will inspect, preview, and prepare your data."
                icon={<Database className="h-5 w-5" />}
            />

            <Card>
                <CardHeader
                    title="Upload CSV"
                    description="Drag and drop or browse to select a .csv file"
                    icon={<Database className="h-5 w-5" />}
                />
                <CardBody>
                    <DatasetUpload />
                </CardBody>
            </Card>

            {dataset && (
                <>
                    <Card>
                        <CardHeader
                            title="Dataset Summary"
                            description="Key information about your uploaded dataset"
                        />
                        <CardBody>
                            <DatasetSummary
                                dataset={dataset}
                                targetColumn={targetColumn}
                                problemType={problemType}
                            />
                        </CardBody>
                    </Card>

                    <Card>
                        <CardHeader
                            title="Target Column"
                            description="Select the column your model will predict"
                        />
                        <CardBody>
                            <div className="max-w-xs">
                                <TargetColumnSelector
                                    value={targetColumn}
                                    onChange={setTargetColumn}
                                    columns={dataset.column_names ?? []}
                                />
                            </div>
                        </CardBody>
                    </Card>

                    <Card>
                        <CardHeader
                            title="Data Preview"
                            description="First rows of your dataset"
                        />
                        <CardBody className="p-0">
                            <DatasetPreview dataset={dataset} />
                        </CardBody>
                    </Card>
                </>
            )}
        </div>
    );
}
