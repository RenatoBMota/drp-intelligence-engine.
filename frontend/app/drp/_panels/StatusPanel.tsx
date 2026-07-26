"use client";

import { useEffect, useMemo, useState } from "react";
import { api, Sku, StatusEstoque } from "@/lib/api";
import { Badge, ErrorBanner, Table } from "@/components/ui";
import { contarOcorrencias, Slicer } from "@/components/Slicer";

const TONE: Record<string, "danger" | "warning" | "success" | "neutral"> = {
  RUPTURA: "danger",
  RUPTURA_DRP: "danger",
  ELEVADA_EXPOSICAO_RUPTURA: "warning",
  BAIXA_EXPOSICAO_RUPTURA: "warning",
  ADEQUADO: "success",
  EXCESSO: "neutral",
};

export default function StatusPanel() {
  const [status, setStatus] = useState<StatusEstoque[]>([]);
  const [skus, setSkus] = useState<Sku[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [statusSelecionado, setStatusSelecionado] = useState<string[]>([]);
  const [eloSelecionado, setEloSelecionado] = useState<string[]>([]);

  useEffect(() => {
    Promise.all([api.drp.status(), api.skus.list()])
      .then(([st, sk]) => {
        setStatus(st);
        setSkus(sk);
      })
      .catch((e) => setErro(String(e)));
  }, []);

  const nomeSku = (id: string) => skus.find((s) => s.id === id)?.codigo ?? id;
  const tipoElo = (s: StatusEstoque) => (s.cd_id ? "cd" : "filial");

  const opcoesStatus = useMemo(() => contarOcorrencias(status, (s) => s.status), [status]);
  const opcoesElo = useMemo(
    () =>
      contarOcorrencias(status, tipoElo).map((o) => ({
        ...o,
        label: o.value === "cd" ? "CD" : "Filial",
      })),
    [status]
  );

  const filtrado = status.filter(
    (s) =>
      (statusSelecionado.length === 0 || statusSelecionado.includes(s.status)) &&
      (eloSelecionado.length === 0 || eloSelecionado.includes(tipoElo(s)))
  );

  return (
    <div>
      <p className="mb-4 text-sm text-slate-400">
        Histórico de snapshots calculados pelo Motor DRP (mais recente primeiro).
      </p>
      {erro && <ErrorBanner message={erro} />}

      <div className="mb-2 grid gap-4 md:grid-cols-2">
        <Slicer label="Status" options={opcoesStatus} selected={statusSelecionado} onChange={setStatusSelecionado} />
        <Slicer label="Tipo de elo" options={opcoesElo} selected={eloSelecionado} onChange={setEloSelecionado} />
      </div>

      <Table headers={["SKU", "Elo", "Necessidade líquida", "Status", "Calculado em"]}>
        {filtrado.map((s) => (
          <tr key={s.id}>
            <td className="px-3 py-2 font-medium">{nomeSku(s.sku_id)}</td>
            <td className="px-3 py-2 text-slate-400">{s.cd_id ? `CD ${s.cd_id.slice(0, 8)}` : `Filial ${s.filial_id?.slice(0, 8)}`}</td>
            <td className="px-3 py-2 text-slate-400">{s.necessidade_liquida}</td>
            <td className="px-3 py-2">
              <Badge tone={TONE[s.status] ?? "neutral"}>{s.status}</Badge>
            </td>
            <td className="px-3 py-2 text-slate-500">{new Date(s.calculado_em).toLocaleString("pt-BR")}</td>
          </tr>
        ))}
      </Table>
      {filtrado.length === 0 && status.length > 0 && (
        <p className="mt-3 text-sm text-slate-500">Nenhum registro corresponde aos filtros selecionados.</p>
      )}
    </div>
  );
}
