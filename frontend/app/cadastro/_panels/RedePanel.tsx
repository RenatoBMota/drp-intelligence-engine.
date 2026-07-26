"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, CentroDistribuicao, Filial } from "@/lib/api";
import { Button, Card, ErrorBanner, Input, Label, Select, Table } from "@/components/ui";

export default function RedePanel() {
  const [cds, setCds] = useState<CentroDistribuicao[]>([]);
  const [filiais, setFiliais] = useState<Filial[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [salvandoCd, setSalvandoCd] = useState(false);
  const [salvandoFilial, setSalvandoFilial] = useState(false);

  const carregar = () =>
    Promise.all([api.centrosDistribuicao.list(), api.filiais.list()])
      .then(([c, f]) => {
        setCds(c);
        setFiliais(f);
      })
      .catch((e) => setErro(String(e)));

  useEffect(() => {
    carregar();
  }, []);

  const onSubmitCd = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formEl = e.currentTarget; // capturado antes do await — depois disso a SyntheticEvent zera currentTarget
    setSalvandoCd(true);
    setErro(null);
    const form = new FormData(formEl);
    try {
      await api.centrosDistribuicao.create({ codigo: String(form.get("codigo")), nome: String(form.get("nome")) });
      formEl.reset();
      await carregar();
    } catch (err) {
      setErro(String(err));
    } finally {
      setSalvandoCd(false);
    }
  };

  const onSubmitFilial = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formEl = e.currentTarget; // capturado antes do await — depois disso a SyntheticEvent zera currentTarget
    setSalvandoFilial(true);
    setErro(null);
    const form = new FormData(formEl);
    const cdSupridorId = String(form.get("cd_supridor_id") || "");
    try {
      await api.filiais.create({
        codigo: String(form.get("codigo")),
        nome: String(form.get("nome")),
        cd_supridor_id: cdSupridorId || null,
      });
      formEl.reset();
      await carregar();
    } catch (err) {
      setErro(String(err));
    } finally {
      setSalvandoFilial(false);
    }
  };

  return (
    <div>
      <p className="mb-4 text-sm text-slate-400">Os elos que o Motor DRP enxerga.</p>
      {erro && <ErrorBanner message={erro} />}

      <div className="mb-6 grid gap-4 md:grid-cols-2">
        <Card>
          <h2 className="mb-3 text-sm font-semibold text-slate-200">Novo Centro de Distribuição</h2>
          <form onSubmit={onSubmitCd} className="flex flex-col gap-3">
            <div className="flex flex-col gap-1">
              <Label>Código *</Label>
              <Input name="codigo" required />
            </div>
            <div className="flex flex-col gap-1">
              <Label>Nome *</Label>
              <Input name="nome" required />
            </div>
            <Button type="submit" disabled={salvandoCd}>
              {salvandoCd ? "Salvando..." : "Criar CD"}
            </Button>
          </form>
        </Card>

        <Card>
          <h2 className="mb-3 text-sm font-semibold text-slate-200">Nova Filial</h2>
          <form onSubmit={onSubmitFilial} className="flex flex-col gap-3">
            <div className="flex flex-col gap-1">
              <Label>Código *</Label>
              <Input name="codigo" required />
            </div>
            <div className="flex flex-col gap-1">
              <Label>Nome *</Label>
              <Input name="nome" required />
            </div>
            <div className="flex flex-col gap-1">
              <Label>CD supridor</Label>
              <Select name="cd_supridor_id" defaultValue="">
                <option value="">(nenhum)</option>
                {cds.map((cd) => (
                  <option key={cd.id} value={cd.id}>
                    {cd.codigo} — {cd.nome}
                  </option>
                ))}
              </Select>
            </div>
            <Button type="submit" disabled={salvandoFilial}>
              {salvandoFilial ? "Salvando..." : "Criar Filial"}
            </Button>
          </form>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <h2 className="mb-2 text-sm font-semibold text-slate-200">Centros de Distribuição</h2>
          <Table headers={["Código", "Nome"]}>
            {cds.map((cd) => (
              <tr key={cd.id}>
                <td className="px-3 py-2">{cd.codigo}</td>
                <td className="px-3 py-2 text-slate-400">{cd.nome}</td>
              </tr>
            ))}
          </Table>
        </div>
        <div>
          <h2 className="mb-2 text-sm font-semibold text-slate-200">Filiais</h2>
          <Table headers={["Código", "Nome", "CD supridor"]}>
            {filiais.map((f) => (
              <tr key={f.id}>
                <td className="px-3 py-2">{f.codigo}</td>
                <td className="px-3 py-2 text-slate-400">{f.nome}</td>
                <td className="px-3 py-2 text-slate-400">
                  {cds.find((c) => c.id === f.cd_supridor_id)?.codigo ?? "—"}
                </td>
              </tr>
            ))}
          </Table>
        </div>
      </div>
    </div>
  );
}
