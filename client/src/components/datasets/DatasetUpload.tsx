import { useRef, useState, type DragEvent } from "react";
import { UploadCloud, FileText, X } from "lucide-react";
import { Button } from "@/src/components/ui/Button";
import { toast } from "sonner";
import { uploadDataset } from "@/src/api/datasets";
import { useWorkflow } from "@/src/context/WorkflowContext";
import type { DatasetInfo } from "@/src/types/types";

export function DatasetUpload() {
    const inputRef = useRef<HTMLInputElement>(null);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [dragging, setDragging] = useState(false);
    const { setDataset, setTargetColumn } = useWorkflow();

    const handleFile = (file: File | null) => {
        if (!file) return;
        if (!file.name.toLowerCase().endsWith(".csv")) {
            setError("Please select a CSV file.");
            setSelectedFile(null);
            return;
        }
        setError(null);
        setSelectedFile(file);
    };

    const onDrop = (e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files?.[0];
        handleFile(file);
    };

    const onUpload = async () => {
        if (!selectedFile) return;
        setLoading(true);
        setError(null);
        try {
            const data = await uploadDataset(selectedFile);
            setDataset(data);
            if (data.column_names && data.column_names.length > 0) {
                setTargetColumn(
                    data.column_names[data.column_names.length - 1],
                );
            }
            toast.success("Dataset uploaded successfully.");
            setSelectedFile(null);
        } catch (err) {
            const message =
                err instanceof Error ? err.message : "Upload failed.";
            setError(message);
            toast.error(message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div
                onDragOver={(e) => {
                    e.preventDefault();
                    setDragging(true);
                }}
                onDragLeave={() => setDragging(false)}
                onDrop={onDrop}
                onClick={() => inputRef.current?.click()}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ")
                        inputRef.current?.click();
                }}
                aria-label="Upload CSV file"
                className={`flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-8 text-center transition-colors ${
                    dragging
                        ? "border-brand-400 bg-brand-50"
                        : "border-slate-300 bg-slate-50 hover:border-brand-300 hover:bg-brand-50/50"
                }`}
            >
                <UploadCloud
                    className="h-10 w-10 text-slate-400"
                    aria-hidden="true"
                />
                <div>
                    <p className="text-sm font-medium text-slate-700">
                        Drag &amp; drop your CSV file here
                    </p>
                    <p className="mt-0.5 text-xs text-slate-400">
                        or click to browse
                    </p>
                </div>
                <input
                    ref={inputRef}
                    type="file"
                    accept=".csv"
                    className="hidden"
                    onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
                />
            </div>

            {selectedFile && (
                <div className="mt-3 flex items-center justify-between rounded-lg border border-slate-200 bg-white p-3">
                    <div className="flex items-center gap-2.5">
                        <FileText
                            className="h-5 w-5 text-brand-500"
                            aria-hidden="true"
                        />
                        <span className="text-sm font-medium text-slate-700">
                            {selectedFile.name}
                        </span>
                        <span className="text-xs text-slate-400">
                            {(selectedFile.size / 1024).toFixed(1)} KB
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Button
                            size="sm"
                            loading={loading}
                            onClick={onUpload}
                            disabled={loading}
                        >
                            Upload
                        </Button>
                        <button
                            onClick={() => setSelectedFile(null)}
                            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
                            aria-label="Remove selected file"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    </div>
                </div>
            )}

            {loading && (
                <p className="mt-3 flex items-center gap-2 text-sm text-brand-600">
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
                    Uploading dataset...
                </p>
            )}

            {error && (
                <p
                    className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700"
                    role="alert"
                >
                    {error}
                </p>
            )}
        </div>
    );
}
