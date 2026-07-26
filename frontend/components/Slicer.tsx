"use client";

export interface SlicerOption {
  value: string;
  label: string;
  count?: number;
}

export function Slicer({
  label,
  options,
  selected,
  onChange,
}: {
  label: string;
  options: SlicerOption[];
  selected: string[];
  onChange: (values: string[]) => void;
}) {
  const toggle = (value: string) => {
    onChange(selected.includes(value) ? selected.filter((v) => v !== value) : [...selected, value]);
  };

  return (
    <div className="mb-4">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</span>
        {selected.length > 0 && (
          <button type="button" onClick={() => onChange([])} className="text-xs text-sky-400 hover:underline">
            Limpar
          </button>
        )}
      </div>
      <div className="flex flex-wrap gap-1.5">
        {options.map((opt) => {
          const active = selected.includes(opt.value);
          return (
            <button
              key={opt.value}
              type="button"
              aria-pressed={active}
              onClick={() => toggle(opt.value)}
              className={`flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
                active
                  ? "border-sky-500 bg-sky-500/15 text-sky-300"
                  : "border-slate-700 text-slate-400 hover:border-slate-600 hover:text-slate-200"
              }`}
            >
              {opt.label}
              {opt.count !== undefined && (
                <span className={`tabular-nums ${active ? "text-sky-400" : "text-slate-500"}`}>{opt.count}</span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

/** Conta ocorrências de uma chave em uma lista, preservando a ordem de primeira aparição. */
export function contarOcorrencias<T>(itens: T[], chave: (item: T) => string): SlicerOption[] {
  const contagem = new Map<string, number>();
  for (const item of itens) {
    const k = chave(item);
    contagem.set(k, (contagem.get(k) ?? 0) + 1);
  }
  return Array.from(contagem.entries()).map(([value, count]) => ({ value, label: value, count }));
}
