"use client";

import { useEffect, useState } from "react";
import { api, OrdemCompra, OrdemTransferencia } from "@/lib/api";
import { Badge, Button, Card, ErrorBanner, PageHeader, Table } from "@/components/ui";

const STATUS_SEGUINTE: Record<string, string | null> = {
  SUGERIDA: "APROVADA",
  APROVADA: "EM_TRANSITO",
  EM_TRANSITO: "CONCLUIDA",
  CONCLUIDA: null,
  CANCELADA: null,
};

export default function OrdensPage() {
  const [transferencias, setTransferencias] = useState<OrdemTransferencia[]>([]);
  const [compras, setCompras] = useState<OrdemCompra[]>([]);
  const [atrasadas, setAtrasadas] = useState<OrdemTransferencia[]>([]);
  const [erro, setErro] = useState<string | null>(null);

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

  return (
    <div>
      <PageHeader title="Ordens" subtitle="Transferências e compras geradas pelo Motor DRP." />
      {erro && <ErrorBanner message={erro} />}

      <Card className="mb-6">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">Ordens de Transferência</h2>
        <Table headers={["Quantidade", "Status", "Chegada estimada", "Score", "", ""]}>
          {transferencias.map((o) => (
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
      </Card>

      <Card>
        <h2 className="mb-3 text-sm font-semibold text-slate-200">Ordens de Compra</h2>
        <Table headers={["Quantidade", "Status", "Previsão", "Score", "", ""]}>
          {compras.map((o) => (
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
      </Card>
    </div>
  );
}
