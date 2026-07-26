"use client";

import type { ReactNode } from "react";

export interface TabDef {
  id: string;
  label: string;
  badge?: ReactNode;
}

export function TabBar({
  tabs,
  active,
  onChange,
}: {
  tabs: TabDef[];
  active: string;
  onChange: (id: string) => void;
}) {
  return (
    <div className="mb-6 flex gap-1 overflow-x-auto border-b border-slate-800" role="tablist">
      {tabs.map((tab) => {
        const isActive = tab.id === active;
        return (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={isActive}
            onClick={() => onChange(tab.id)}
            className={`relative flex shrink-0 items-center gap-2 px-3.5 py-2.5 text-sm font-medium transition-colors ${
              isActive ? "text-sky-400" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {tab.label}
            {tab.badge !== undefined && (
              <span
                className={`rounded px-1.5 py-0.5 text-xs font-medium tabular-nums ${
                  isActive ? "bg-sky-950 text-sky-300" : "bg-slate-800 text-slate-400"
                }`}
              >
                {tab.badge}
              </span>
            )}
            <span
              className={`absolute inset-x-0 -bottom-px h-0.5 rounded-full transition-colors ${
                isActive ? "bg-sky-400" : "bg-transparent"
              }`}
            />
          </button>
        );
      })}
    </div>
  );
}
