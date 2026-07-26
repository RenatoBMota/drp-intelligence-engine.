"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, CentroDistribuicao, Filial, SaldoEstoque, Sku } from "@/lib/api";
import { Button, Card, ErrorBanner, Input, Label, PageHeader, Select, Table } from "@/components/ui";

export default function EstoquePage() {
  const [saldos, setSaldos] = useState<SaldoEstoque[]>([]);
  const [skus, setSkus] = useState<Sku[]>([]);
  const [cds, setCds] = useState<CentroDistribuicao[]>([]);
  const [filiais, setFiliais] = useState<Filial[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);
  const [tipoElo, setTipoElo] = useState<"cd" | "filial">("filial");

  const carregar = () =>
    Promise.all([api.estoque.list(), api.skus.list(), api.centrosDistribuicao.list(), api.filiais.list()])
      .then(([s, sk, c, f]) => {
        setSaldos(s);
        setSkus(sk);
        setCds(c);
        setFiliais(f);
      })
      .catch((e) => setErro(String(e)));

  useEffect(() => {
    carregar();
  }, []);

  const nomeSku = (id: string) => skus.find((s) => s.id === id)?.codigo ?? id;
  const nomeElo = (cdId: string | null, filialId: string | null) => {
    if (cdId) return `CD ${cds.find((c) => c.id === cdId)?.codigo ?? cdId}`;
    if (filialId) return `Filial ${filiais.find((f) => f.id === filialId)?.codigo ?? filialId}`;
    return "—";
  };

  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formEl = e.currentTarget; // capturado antes do await — depois disso a SyntheticEvent zera currentTarget
    setSalvando(true);
    setErro(null);
    const form = new FormData(formEl);
    try {
      await api.estoque.set({
        sku_id: String(form.get("sku_id")),
        cd_id: tipoElo === "cd" ? String(form.get("elo_id")) : undefined,
        filial_id: tipoElo === "filial" ? String(form.get("elo_id")) : undefined,
        quantidade: Number(form.get("quantidade")),
      });
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
      <PageHeader title="Estoque" subtitle="Saldo disponível por SKU e elo (CD ou Filial)." />
      {erro && <ErrorBanner message={erro} />}

      <Card className="mb-6">
        <form onSubmit={onSubmit} className="grid grid-cols-1 gap-3 md:grid-cols-5">
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
          <div className="flex flex-col gap-1">
            <Label>Quantidade *</Label>
            <Input name="quantidade" type="number" min={0} step="0.01" required />
          </div>
          <div className="flex items-end">
            <Button type="submit" disabled={salvando}>
              {salvando ? "Salvando..." : "Definir saldo"}
            </Button>
          </div>
        </form>
        <p className="mt-2 text-xs text-slate-500">
          Definir o saldo é um upsert: se já existir um registro para o mesmo SKU/elo, ele é atualizado.
        </p>
      </Card>

      <Table headers={["SKU", "Elo", "Quantidade"]}>
        {saldos.map((s) => (
          <tr key={s.id}>
            <td className="px-3 py-2 font-medium">{nomeSku(s.sku_id)}</td>
            <td className="px-3 py-2 text-slate-400">{nomeElo(s.cd_id, s.filial_id)}</td>
            <td className="px-3 py-2 text-slate-400">{s.quantidade}</td>
          </tr>
        ))}
      </Table>
    </div>
  );
}
