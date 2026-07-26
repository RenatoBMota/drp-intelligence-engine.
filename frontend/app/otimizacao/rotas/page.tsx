"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, CentroDistribuicao, Filial, Rota } from "@/lib/api";
import { Button, Card, ErrorBanner, Input, Label, PageHeader, Select, Table } from "@/components/ui";

type TipoElo = "cd" | "filial";

export default function RotasPage() {
  const [rotas, setRotas] = useState<Rota[]>([]);
  const [cds, setCds] = useState<CentroDistribuicao[]>([]);
  const [filiais, setFiliais] = useState<Filial[]>([]);
  const [tipoOrigem, setTipoOrigem] = useState<TipoElo>("cd");
  const [tipoDestino, setTipoDestino] = useState<TipoElo>("filial");
  const [erro, setErro] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);

  const carregar = () =>
    Promise.all([api.otimizacao.rotas.list(), api.centrosDistribuicao.list(), api.filiais.list()])
      .then(([r, c, f]) => {
        setRotas(r);
        setCds(c);
        setFiliais(f);
      })
      .catch((e) => setErro(String(e)));

  useEffect(() => {
    carregar();
  }, []);

  const nomeElo = (cdId: string | null, filialId: string | null) => {
    if (cdId) return `CD ${cds.find((c) => c.id === cdId)?.codigo ?? cdId.slice(0, 8)}`;
    if (filialId) return `Filial ${filiais.find((f) => f.id === filialId)?.codigo ?? filialId.slice(0, 8)}`;
    return "—";
  };

  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formEl = e.currentTarget; // capturado antes do await — depois disso a SyntheticEvent zera currentTarget
    setSalvando(true);
    setErro(null);
    const form = new FormData(formEl);
    try {
      await api.otimizacao.rotas.create({
        origem_cd_id: tipoOrigem === "cd" ? String(form.get("origem_id")) : null,
        origem_filial_id: tipoOrigem === "filial" ? String(form.get("origem_id")) : null,
        destino_cd_id: tipoDestino === "cd" ? String(form.get("destino_id")) : null,
        destino_filial_id: tipoDestino === "filial" ? String(form.get("destino_id")) : null,
        capacidade_maxima: Number(form.get("capacidade_maxima")),
        custo_unitario: Number(form.get("custo_unitario")),
        lead_time_dias: Number(form.get("lead_time_dias")),
      } as Partial<Rota>);
      formEl.reset();
      await carregar();
    } catch (err) {
      setErro(String(err));
    } finally {
      setSalvando(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Rotas"
        subtitle="Capacidade, custo e lead time de transporte entre elos — usadas pela otimização de rede."
      />
      {erro && <ErrorBanner message={erro} />}

      <Card className="mb-6">
        <form onSubmit={onSubmit} className="grid grid-cols-1 gap-3 md:grid-cols-3">
          <div className="flex flex-col gap-1">
            <Label>Origem (tipo)</Label>
            <Select value={tipoOrigem} onChange={(e) => setTipoOrigem(e.target.value as TipoElo)}>
              <option value="cd">CD</option>
              <option value="filial">Filial</option>
            </Select>
          </div>
          <div className="flex flex-col gap-1 md:col-span-2">
            <Label>Origem *</Label>
            <Select name="origem_id" required defaultValue="">
              <option value="" disabled>
                Selecione
              </option>
              {(tipoOrigem === "cd" ? cds : filiais).map((e) => (
                <option key={e.id} value={e.id}>
                  {e.codigo} — {e.nome}
                </option>
              ))}
            </Select>
          </div>

          <div className="flex flex-col gap-1">
            <Label>Destino (tipo)</Label>
            <Select value={tipoDestino} onChange={(e) => setTipoDestino(e.target.value as TipoElo)}>
              <option value="cd">CD</option>
              <option value="filial">Filial</option>
            </Select>
          </div>
          <div className="flex flex-col gap-1 md:col-span-2">
            <Label>Destino *</Label>
            <Select name="destino_id" required defaultValue="">
              <option value="" disabled>
                Selecione
              </option>
              {(tipoDestino === "cd" ? cds : filiais).map((e) => (
                <option key={e.id} value={e.id}>
                  {e.codigo} — {e.nome}
                </option>
              ))}
            </Select>
          </div>

          <div className="flex flex-col gap-1">
            <Label>Capacidade máxima *</Label>
            <Input name="capacidade_maxima" type="number" min={0} step="0.01" required />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Custo unitário *</Label>
            <Input name="custo_unitario" type="number" min={0} step="0.01" required />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Lead time (dias) *</Label>
            <Input name="lead_time_dias" type="number" min={0} required />
          </div>

          <div className="md:col-span-3">
            <Button type="submit" disabled={salvando}>
              {salvando ? "Salvando..." : "Criar rota"}
            </Button>
          </div>
        </form>
      </Card>

      <Table headers={["Origem", "Destino", "Capacidade", "Custo unit.", "Lead time", "Ativa"]}>
        {rotas.map((r) => (
          <tr key={r.id}>
            <td className="px-3 py-2">{nomeElo(r.origem_cd_id, r.origem_filial_id)}</td>
            <td className="px-3 py-2">{nomeElo(r.destino_cd_id, r.destino_filial_id)}</td>
            <td className="px-3 py-2 text-slate-400">{r.capacidade_maxima}</td>
            <td className="px-3 py-2 text-slate-400">{r.custo_unitario}</td>
            <td className="px-3 py-2 text-slate-400">{r.lead_time_dias}d</td>
            <td className="px-3 py-2 text-slate-400">{r.ativa ? "Sim" : "Não"}</td>
          </tr>
        ))}
      </Table>
    </div>
  );
}
