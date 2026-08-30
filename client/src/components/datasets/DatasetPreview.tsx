import { Table } from "lucide-react";
import type { DatasetInfo } from "@/src/types/types";

export function DatasetPreview({ dataset }: { dataset: DatasetInfo }) {
    const columns = dataset.column_names ?? [];
    const rows = dataset.preview ?? [];

    if (rows.length === 0) {
        return (
            <p className="py-6 text-center text-sm text-slate-400">
                No preview data available.
            </p>
        );
    }

    return (
        <div className="overflow-x-auto scrollbar-thin">
            <table className="min-w-full border-separate border-spacing-0 text-sm">
                <thead>
                    <tr>
                        {columns.map((col, i) => (
                            <th
                                key={`${col}-${i}`}
                                className="sticky top-0 border-b border-slate-200 bg-slate-50 px-4 py-2.5 text-left font-semibold text-slate-700 whitespace-nowrap"
                            >
                                {col}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {rows.map((row, ri) => (
                        <tr key={ri} className="hover:bg-slate-50">
                            {columns.map((col, ci) => (
                                <td
                                    key={`${col}-${ci}`}
                                    className="border-b border-slate-100 px-4 py-2.5 text-slate-600 whitespace-nowrap"
                                >
                                    {String(row[col] ?? "")}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
            <div className="mt-2 flex items-center gap-1.5 px-1 text-xs text-slate-400">
                <Table className="h-3.5 w-3.5" aria-hidden="true" />
                Showing {rows.length} of {dataset.rows} rows · {columns.length}{" "}
                columns
            </div>
        </div>
    );
}
