"use client";

import { useEffect, useMemo, useState } from "react";
import { api, OrdemCompra, OrdemTransferencia } from "@/lib/api";
import { Badge, Button, Card, ErrorBanner, Table } from "@/components/ui";
import { contarOcorrencias, Slicer } from "@/components/Slicer";

const STATUS_SEGUINTE: Record<string, string | null> = {
  SUGERIDA: "APROVADA",
  APROVADA: "EM_TRANSITO",
  EM_TRANSITO: "CONCLUIDA",
  CONCLUIDA: null,
  CANCELADA: null,
};

export default function OrdensPanel() {
  const [transferencias, setTransferencias] = useState<OrdemTransferencia[]>([]);
  const [compras, setCompras] = useState<OrdemCompra[]>([]);
  const [atrasadas, setAtrasadas] = useState<OrdemTransferencia[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [statusSelecionado, setStatusSelecionado] = useState<string[]>([]);

  const carregar = () =>
    Promise.all([api.drp.ordensTransferencia(), api.drp.ordensCompra(), api.drp.alertasDesvio()])
      .then(([t, c, a]) => {
        setTransferencias(t);
        setCompras(c);
        setAtrasadas(a);
      })
      .catch((e) => setErro(String(e)));

  useEffect(() => {
    carregar();
  }, []);

  const avancarTransferencia = async (ordem: OrdemTransferencia) => {
    const proximo = STATUS_SEGUINTE[ordem.status];
    if (!proximo) return;
    try {
      await api.drp.atualizarOrdemTransferencia(ordem.id, proximo, proximo === "CONCLUIDA" ? new Date().toISOString().slice(0, 10) : undefined);
      await carregar();
    } catch (err) {
      setErro(String(err));
    }
  };

  const avancarCompra = async (ordem: OrdemCompra) => {
    const proximo = STATUS_SEGUINTE[ordem.status];
    if (!proximo) return;
    try {
      await api.drp.atualizarOrdemCompra(ordem.id, proximo, proximo === "CONCLUIDA" ? new Date().toISOString().slice(0, 10) : undefined);
      await carregar();
    } catch (err) {
      setErro(String(err));
    }
  };

  const idsAtrasadas = new Set(atrasadas.map((o) => o.id));

  const opcoesStatus = useMemo(
    () => contarOcorrencias([...transferencias, ...compras], (o) => o.status),
    [transferencias, compras]
  );

  const transferenciasFiltradas = transferencias.filter(
    (o) => statusSelecionado.length === 0 || statusSelecionado.includes(o.status)
  );
  const comprasFiltradas = compras.filter((o) => statusSelecionado.length === 0 || statusSelecionado.includes(o.status));

  return (
    <div>
      <p className="mb-4 text-sm text-slate-400">Transferências e compras geradas pelo Motor DRP.</p>
      {erro && <ErrorBanner message={erro} />}

      <Slicer label="Status" options={opcoesStatus} selected={statusSelecionado} onChange={setStatusSelecionado} />

      <Card className="mb-6">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">Ordens de Transferência</h2>
        <Table headers={["Quantidade", "Status", "Chegada estimada", "Score", "", ""]}>
          {transferenciasFiltradas.map((o) => (
            <tr key={o.id}>
              <td className="px-3 py-2">{o.quantidade}</td>
              <td className="px-3 py-2">
                <Badge tone={idsAtrasadas.has(o.id) ? "danger" : "neutral"}>
                  {o.status}
                  {idsAtrasadas.has(o.id) ? " · atrasada" : ""}
                </Badge>
              </td>
              <td className="px-3 py-2 text-slate-400">{o.data_chegada_estimada}</td>
              <td className="px-3 py-2 text-slate-400">{o.score_criticidade.toFixed(2)}</td>
              <td className="px-3 py-2">
                {STATUS_SEGUINTE[o.status] && (
                  <Button variant="secondary" onClick={() => avancarTransferencia(o)}>
                    Avançar → {STATUS_SEGUINTE[o.status]}
                  </Button>
                )}
              </td>
              <td className="px-3 py-2 text-xs text-slate-500">{o.justificativa}</td>
            </tr>
          ))}
        </Table>
        {transferenciasFiltradas.length === 0 && transferencias.length > 0 && (
          <p className="mt-3 text-sm text-slate-500">Nenhuma transferência corresponde ao filtro selecionado.</p>
        )}
      </Card>

      <Card>
        <h2 className="mb-3 text-sm font-semibold text-slate-200">Ordens de Compra</h2>
        <Table headers={["Quantidade", "Status", "Previsão", "Score", "", ""]}>
          {comprasFiltradas.map((o) => (
            <tr key={o.id}>
              <td className="px-3 py-2">{o.quantidade}</td>
              <td className="px-3 py-2">
                <Badge>{o.status}</Badge>
              </td>
              <td className="px-3 py-2 text-slate-400">{o.data_previsao}</td>
              <td className="px-3 py-2 text-slate-400">{o.score_criticidade.toFixed(2)}</td>
              <td className="px-3 py-2">
                {STATUS_SEGUINTE[o.status] && (
                  <Button variant="secondary" onClick={() => avancarCompra(o)}>
                    Avançar → {STATUS_SEGUINTE[o.status]}
                  </Button>
                )}
              </td>
              <td className="px-3 py-2 text-xs text-slate-500">{o.justificativa}</td>
            </tr>
          ))}
        </Table>
        {comprasFiltradas.length === 0 && compras.length > 0 && (
          <p className="mt-3 text-sm text-slate-500">Nenhuma compra corresponde ao filtro selecionado.</p>
        )}
      </Card>
    </div>
  );
}
