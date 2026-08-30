interface ModelSelectorProps {
    value: string;
    onChange: (model: string) => void;
    options: string[];
    label?: string;
    disabled?: boolean;
}

export function ModelSelector({
    value,
    onChange,
    options,
    label = "Model",
    disabled,
}: ModelSelectorProps) {
    return (
        <div>
            <label
                htmlFor="model-select"
                className="mb-1.5 block text-sm font-medium text-slate-700"
            >
                {label}
            </label>
            <select
                id="model-select"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                disabled={disabled}
                className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-800 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
                {options.map((opt) => (
                    <option key={opt} value={opt}>
                        {opt}
                    </option>
                ))}
            </select>
        </div>
    );
}
