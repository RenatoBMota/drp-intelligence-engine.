"use client";

import { FormEvent } from "react";
import { Button, Card, Input, Label } from "@/components/ui";
import { CONFIG_PADRAO, ConfiguracaoMetricas } from "@/lib/config";

export interface CampoConfig {
  chave: keyof ConfiguracaoMetricas;
  label: string;
  step?: string;
  hint: string;
}

export function ConfigForm({
  campos,
  config,
  atualizar,
}: {
  campos: CampoConfig[];
  config: ConfiguracaoMetricas;
  atualizar: (novo: ConfiguracaoMetricas) => void;
}) {
  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const novo = { ...config };
    for (const campo of campos) {
      (novo[campo.chave] as number) = Number(form.get(campo.chave));
    }
    atualizar(novo);
  };

  const restaurarPadrao = () => {
    const novo = { ...config };
    for (const campo of campos) {
      (novo[campo.chave] as number) = CONFIG_PADRAO[campo.chave] as number;
    }
    atualizar(novo);
  };

  return (
    <Card>
      <form key={campos.map((c) => c.chave).join(",")} onSubmit={onSubmit} className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {campos.map((campo) => (
          <div key={campo.chave} className="flex flex-col gap-1">
            <Label>{campo.label}</Label>
            <Input name={campo.chave} type="number" step={campo.step ?? "1"} defaultValue={config[campo.chave]} />
            {campo.hint && <span className="text-xs text-slate-500">{campo.hint}</span>}
          </div>
        ))}

        <div className="flex gap-2 md:col-span-2">
          <Button type="submit">Salvar</Button>
          <Button type="button" variant="secondary" onClick={restaurarPadrao}>
            Restaurar padrão
          </Button>
        </div>
      </form>
    </Card>
  );
}
