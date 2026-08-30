interface TargetColumnSelectorProps {
    value: string;
    onChange: (col: string) => void;
    columns: string[];
    disabled?: boolean;
}

export function TargetColumnSelector({
    value,
    onChange,
    columns,
    disabled,
}: TargetColumnSelectorProps) {
    return (
        <div>
            <label
                htmlFor="target-select"
                className="mb-1.5 block text-sm font-medium text-slate-700"
            >
                Target Column
            </label>
            <select
                id="target-select"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                disabled={disabled || columns.length === 0}
                className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-800 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
                {columns.length === 0 && (
                    <option value="">No columns available</option>
                )}
                {columns.map((col) => (
                    <option key={col} value={col}>
                        {col}
                    </option>
                ))}
            </select>
        </div>
    );
}
