import { useState } from "react";
import { FileBarChart, ExternalLink, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/src/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/src/components/ui/Card";
import { LoadingState } from "@/src/components/ui/LoadingState";
import { ErrorState } from "@/src/components/ui/ErrorState";
import { EmptyState } from "@/src/components/ui/EmptyState";
import { generateProfile, buildProfileUrl } from "@/src/api/profiling";
import { buildApiUrl } from "@/src/api/client";
import { useWorkflow } from "@/src/context/WorkflowContext";
import type { ProfileResponse } from "@/src/types/types";

function extractFilename(res: ProfileResponse): string {
    return (
        res.filename ||
        (typeof res.profile_path === "string"
            ? (res.profile_path as string).split("/").pop()
            : "") ||
        ""
    );
}

export function ProfilingPanel() {
    const {
        dataset,
        profile,
        setProfile,
        profileFilename,
        setProfileFilename,
    } = useWorkflow();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleGenerate = async () => {
        if (!dataset) return;
        setLoading(true);
        setError(null);
        try {
            const res = await generateProfile(dataset.dataset_id);
            const filename = extractFilename(res);
            setProfile(res);
            setProfileFilename(filename);
            toast.success("Profile generated successfully.");
        } catch (err) {
            const message =
                err instanceof Error
                    ? err.message
                    : "Failed to generate profile.";
            setError(message);
            toast.error(message);
        } finally {
            setLoading(false);
        }
    };

    if (!dataset) {
        return (
            <EmptyState
                icon={<FileBarChart className="h-10 w-10" />}
                title="No dataset loaded"
                description="Upload a dataset first to generate a profile report."
            />
        );
    }

    const profileSrc = profileFilename
        ? buildApiUrl(buildProfileUrl(profileFilename))
        : profile?.profile_url
          ? buildApiUrl(profile.profile_url)
          : "";

    return (
        <div className="space-y-4">
            <Card>
                <CardHeader
                    title="Dataset Profiling"
                    description="Generate a detailed statistical profile of your dataset using pandas-profiling."
                    icon={<FileBarChart className="h-5 w-5" />}
                    action={
                        <Button
                            onClick={handleGenerate}
                            loading={loading}
                            disabled={loading}
                        >
                            <RefreshCw className="h-4 w-4" />
                            {profile
                                ? "Regenerate Profile"
                                : "Generate Profile"}
                        </Button>
                    }
                />
                <CardBody>
                    {loading && (
                        <LoadingState message="Generating profile..." />
                    )}
                    {!loading && error && (
                        <ErrorState
                            message="Profiling failed"
                            detail={error}
                            onRetry={handleGenerate}
                        />
                    )}
                    {!loading && !error && !profile && (
                        <EmptyState
                            icon={<FileBarChart className="h-10 w-10" />}
                            title="No profile generated yet"
                            description="Click 'Generate Profile' to create a detailed report for your dataset."
                        />
                    )}
                </CardBody>
            </Card>

            {profileSrc && !loading && !error && (
                <Card>
                    <CardHeader
                        title="Profile Report"
                        description="Embedded report view"
                        icon={<FileBarChart className="h-5 w-5" />}
                        action={
                            <a
                                href={profileSrc}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <Button variant="outline" size="sm">
                                    <ExternalLink className="h-4 w-4" />
                                    Open in new tab
                                </Button>
                            </a>
                        }
                    />
                    <CardBody className="p-0">
                        <iframe
                            src={profileSrc}
                            title="Dataset Profile Report"
                            className="h-150 w-full rounded-b-xl border-0"
                            sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
                        />
                    </CardBody>
                </Card>
            )}
        </div>
    );
}
