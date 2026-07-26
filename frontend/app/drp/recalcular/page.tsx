"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, CentroDistribuicao, Filial, Sku } from "@/lib/api";
import { Badge, Button, Card, ErrorBanner, Label, PageHeader, Select } from "@/components/ui";
import { pesosPriorizacao, useConfiguracao } from "@/lib/config";

type Resultado = Awaited<ReturnType<typeof api.drp.recalcular>>;

export default function RecalcularPage() {
  const [skus, setSkus] = useState<Sku[]>([]);
  const [cds, setCds] = useState<CentroDistribuicao[]>([]);
  const [filiais, setFiliais] = useState<Filial[]>([]);
  const [tipoElo, setTipoElo] = useState<"cd" | "filial">("filial");
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [calculando, setCalculando] = useState(false);
  const { config } = useConfiguracao();

  useEffect(() => {
    Promise.all([api.skus.list(), api.centrosDistribuicao.list(), api.filiais.list()]).then(
      ([s, c, f]) => {
        setSkus(s);
        setCds(c);
        setFiliais(f);
      }
    );
  }, []);

  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setCalculando(true);
    setErro(null);
    setResultado(null);
    const form = new FormData(e.currentTarget);
    try {
      const r = await api.drp.recalcular({
        sku_id: String(form.get("sku_id")),
        cd_id: tipoElo === "cd" ? String(form.get("elo_id")) : undefined,
        filial_id: tipoElo === "filial" ? String(form.get("elo_id")) : undefined,
        pesos_priorizacao: pesosPriorizacao(config),
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
        title="Recalcular Motor DRP"
        subtitle="Necessidade líquida → status de ruptura → decisão de ressuprimento, para um SKU/elo."
      />
      {erro && <ErrorBanner message={erro} />}

      <Card className="mb-6">
        <form onSubmit={onSubmit} className="grid grid-cols-1 gap-3 md:grid-cols-4">
          <div className="flex flex-col gap-1">
            <Label>SKU *</Label>
            <Select name="sku_id" required defaultValue="">
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
            <Label>Tipo de elo</Label>
            <Select value={tipoElo} onChange={(e) => setTipoElo(e.target.value as "cd" | "filial")}>
              <option value="filial">Filial</option>
              <option value="cd">CD</option>
            </Select>
          </div>
          <div className="flex flex-col gap-1">
            <Label>Elo *</Label>
            <Select name="elo_id" required defaultValue="">
              <option value="" disabled>
                Selecione
              </option>
              {(tipoElo === "cd" ? cds : filiais).map((e) => (
                <option key={e.id} value={e.id}>
                  {e.codigo} — {e.nome}
                </option>
              ))}
            </Select>
          </div>
          <div className="flex items-end">
            <Button type="submit" disabled={calculando}>
              {calculando ? "Calculando..." : "Recalcular"}
            </Button>
          </div>
        </form>
        <p className="mt-2 text-xs text-slate-500">
          Usa os pesos de priorização definidos em Configurações (w1={config.pesoW1Criticidade}, w2=
          {config.pesoW2Custo}, w3={config.pesoW3InversoCobertura}, w4={config.pesoW4Frequencia}).
        </p>
      </Card>

      {resultado && (
        <Card className="flex flex-col gap-4">
          <div>
            <h2 className="mb-2 text-sm font-semibold text-slate-200">Status de estoque</h2>
            <div className="flex items-center gap-3 text-sm">
              <Badge tone={resultado.status_estoque.status.includes("RUPTURA") ? "danger" : "neutral"}>
                {resultado.status_estoque.status}
              </Badge>
              <span className="text-slate-400">
                Necessidade líquida: <span className="text-slate-200">{resultado.status_estoque.necessidade_liquida}</span>
              </span>
            </div>
          </div>

          {resultado.silenciado_motivo && (
            <div className="text-sm text-amber-400">
              Nenhuma ordem gerada — SKU silenciado/inativo: {resultado.silenciado_motivo}
            </div>
          )}

          {resultado.ordem_transferencia && (
            <div>
              <h2 className="mb-2 text-sm font-semibold text-slate-200">Ordem de Transferência gerada</h2>
              <p className="text-sm text-slate-300">
                Quantidade: {resultado.ordem_transferencia.quantidade} — Score:{" "}
                {resultado.ordem_transferencia.score_criticidade.toFixed(2)}
              </p>
              <p className="text-sm text-slate-500">{resultado.ordem_transferencia.justificativa}</p>
            </div>
          )}

          {resultado.ordem_compra && (
            <div>
              <h2 className="mb-2 text-sm font-semibold text-slate-200">Ordem de Compra gerada</h2>
              <p className="text-sm text-slate-300">
                Quantidade: {resultado.ordem_compra.quantidade} — Score:{" "}
                {resultado.ordem_compra.score_criticidade.toFixed(2)}
              </p>
              <p className="text-sm text-slate-500">{resultado.ordem_compra.justificativa}</p>
            </div>
          )}

          {!resultado.ordem_transferencia && !resultado.ordem_compra && !resultado.silenciado_motivo && (
            <p className="text-sm text-slate-500">Necessidade líquida não positiva — nenhuma ordem necessária.</p>
          )}
        </Card>
      )}
    </div>
  );
}
