"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, ResultadoOtimizacao, Rota, Sku } from "@/lib/api";
import { Badge, Button, Card, ErrorBanner, Input, Label, PageHeader, Select, Table } from "@/components/ui";
import { useConfiguracao } from "@/lib/config";

export default function OtimizarPage() {
  const [skus, setSkus] = useState<Sku[]>([]);
  const [rotas, setRotas] = useState<Rota[]>([]);
  const [skuId, setSkuId] = useState("");
  const [resultado, setResultado] = useState<ResultadoOtimizacao | null>(null);
  const [modo, setModo] = useState<"real" | "simulacao">("real");
  const [rotaDesativada, setRotaDesativada] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [calculando, setCalculando] = useState(false);
  const { config } = useConfiguracao();

  useEffect(() => {
    Promise.all([api.skus.list(), api.otimizacao.rotas.list()]).then(([s, r]) => {
      setSkus(s);
      setRotas(r);
    });
  }, []);

  const executar = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!skuId) return;
    setCalculando(true);
    setErro(null);
    setResultado(null);
    try {
      const r =
        modo === "real"
          ? await api.otimizacao.otimizar(skuId, config.custoCompraExterna)
          : await api.otimizacao.simular(skuId, {
              rotas_desativadas: rotaDesativada ? [rotaDesativada] : [],
              custo_compra_externa: config.custoCompraExterna,
            });
      setResultado(r);
    } catch (err) {
      setErro(String(err));
    } finally {
      setCalculando(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Otimização de Rede / Simulação de Cenários"
        subtitle="Programação Linear: aloca excedente aos elos com necessidade minimizando custo total, respeitando capacidade de rota."
      />
      {erro && <ErrorBanner message={erro} />}

      <Card className="mb-6">
        <form onSubmit={executar} className="grid grid-cols-1 gap-3 md:grid-cols-4">
          <div className="flex flex-col gap-1">
            <Label>SKU *</Label>
            <Select value={skuId} onChange={(e) => setSkuId(e.target.value)} required>
              <option value="" disabled>
                Selecione
              </option>
              {skus.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.codigo}
                </option>
              ))}
            </Select>
          </div>
          <div className="flex flex-col gap-1">
            <Label>Modo</Label>
            <Select value={modo} onChange={(e) => setModo(e.target.value as "real" | "simulacao")}>
              <option value="real">Otimização real</option>
              <option value="simulacao">Simulação (what-if)</option>
            </Select>
          </div>
          {modo === "simulacao" && (
            <div className="flex flex-col gap-1">
              <Label>Desativar rota</Label>
              <Select value={rotaDesativada} onChange={(e) => setRotaDesativada(e.target.value)}>
                <option value="">(nenhuma)</option>
                {rotas.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.id.slice(0, 8)}… (cap. {r.capacidade_maxima}, custo {r.custo_unitario})
                  </option>
                ))}
              </Select>
            </div>
          )}
          <div className="flex items-end">
            <Button type="submit" disabled={calculando}>
              {calculando ? "Calculando..." : modo === "real" ? "Otimizar" : "Simular"}
            </Button>
          </div>
        </form>
        <p className="mt-2 text-xs text-slate-500">
          Custo de compra externa (penalidade): {config.custoCompraExterna} — ajustável em Configurações.
        </p>
      </Card>

      {resultado && (
        <Card>
          <div className="mb-4 grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="block text-xs uppercase text-slate-500">Custo total</span>
              <span className="text-lg font-semibold">{resultado.custo_total.toFixed(2)}</span>
            </div>
            <div>
              <span className="block text-xs uppercase text-slate-500">Via rede</span>
              <span className="text-lg font-semibold text-emerald-400">{resultado.quantidade_via_rede.toFixed(1)}</span>
            </div>
            <div>
              <span className="block text-xs uppercase text-slate-500">Via compra externa</span>
              <span className="text-lg font-semibold text-amber-400">
                {resultado.quantidade_via_compra_externa.toFixed(1)}
              </span>
            </div>
          </div>

          <Table headers={["Origem", "Destino", "Quantidade", "Custo unitário"]}>
            {resultado.fluxos.map((f, i) => (
              <tr key={i}>
                <td className="px-3 py-2">
                  {f.origem === "EXTERNO" ? <Badge tone="warning">EXTERNO</Badge> : f.origem}
                </td>
                <td className="px-3 py-2">{f.destino}</td>
                <td className="px-3 py-2 text-slate-400">{f.quantidade.toFixed(1)}</td>
                <td className="px-3 py-2 text-slate-400">{f.custo_unitario}</td>
              </tr>
            ))}
          </Table>
          {resultado.fluxos.length === 0 && (
            <p className="text-sm text-slate-500">Nenhuma necessidade a resolver para este SKU no momento.</p>
          )}
        </Card>
      )}
    </div>
  );
}
