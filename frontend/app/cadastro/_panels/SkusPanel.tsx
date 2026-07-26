"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, Fornecedor, Sku } from "@/lib/api";
import { Badge, Button, Card, ErrorBanner, Input, Label, Select, Table } from "@/components/ui";

export default function SkusPanel() {
  const [skus, setSkus] = useState<Sku[]>([]);
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);

  const carregar = () =>
    Promise.all([api.skus.list(), api.fornecedores.list()])
      .then(([s, f]) => {
        setSkus(s);
        setFornecedores(f);
      })
      .catch((e) => setErro(String(e)));

  useEffect(() => {
    carregar();
  }, []);

  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formEl = e.currentTarget; // capturado antes do await — depois disso a SyntheticEvent zera currentTarget
    setSalvando(true);
    setErro(null);
    const form = new FormData(formEl);
    const num = (campo: string) => {
      const v = form.get(campo);
      return v ? Number(v) : null;
    };
    try {
      await api.skus.create({
        codigo: String(form.get("codigo")),
        descricao: String(form.get("descricao")),
        fornecedor_id: String(form.get("fornecedor_id") || "") || null,
        criticidade_resultado: String(form.get("criticidade_resultado") || "") || null,
        custo_aquisicao: String(form.get("custo_aquisicao") || "") || null,
        frequencia_saida: String(form.get("frequencia_saida") || "") || null,
        perfil_demanda: String(form.get("perfil_demanda") || "") || null,
        lead_time_dias: num("lead_time_dias"),
        estoque_seguranca: num("estoque_seguranca"),
        ponto_pedido: num("ponto_pedido"),
        estoque_maximo: num("estoque_maximo"),
      } as Partial<Sku>);
      formEl.reset();
      await carregar();
    } catch (err) {
      setErro(String(err));
    } finally {
      setSalvando(false);
    }
  };

  const toggleAtivo = async (sku: Sku) => {
    try {
      await api.skus.setAtivo(sku.id, !sku.ativo);
      await carregar();
    } catch (err) {
      setErro(String(err));
    }
  };

  return (
    <div>
      <p className="mb-4 text-sm text-slate-400">
        Ficha de produto: parâmetros de reposição e classificações (roadmap seção 4.6).
      </p>
      {erro && <ErrorBanner message={erro} />}

      <Card className="mb-6">
        <form onSubmit={onSubmit} className="grid grid-cols-1 gap-3 md:grid-cols-4">
          <div className="flex flex-col gap-1">
            <Label>Código *</Label>
            <Input name="codigo" required />
          </div>
          <div className="flex flex-col gap-1 md:col-span-2">
            <Label>Descrição *</Label>
            <Input name="descricao" required />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Fornecedor</Label>
            <Select name="fornecedor_id" defaultValue="">
              <option value="">(nenhum)</option>
              {fornecedores.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.razao_social}
                </option>
              ))}
            </Select>
          </div>

          <div className="flex flex-col gap-1">
            <Label>Criticidade de Resultado</Label>
            <Select name="criticidade_resultado" defaultValue="">
              <option value="">—</option>
              <option value="VITAL">Vital</option>
              <option value="INTERMEDIARIO">Intermediário</option>
              <option value="ORDINARIO">Ordinário</option>
            </Select>
          </div>
          <div className="flex flex-col gap-1">
            <Label>Custo de Aquisição</Label>
            <Select name="custo_aquisicao" defaultValue="">
              <option value="">—</option>
              <option value="ELEVADO">Elevado</option>
              <option value="INTERMEDIARIO">Intermediário</option>
              <option value="BAIXO">Baixo</option>
            </Select>
          </div>
          <div className="flex flex-col gap-1">
            <Label>Frequência de Saída</Label>
            <Select name="frequencia_saida" defaultValue="">
              <option value="">—</option>
              <option value="POPULAR">Popular</option>
              <option value="INTERMEDIARIA">Intermediária</option>
              <option value="RARO">Raro</option>
            </Select>
          </div>
          <div className="flex flex-col gap-1">
            <Label>Perfil de Demanda</Label>
            <Select name="perfil_demanda" defaultValue="">
              <option value="">—</option>
              <option value="REPETITIVO">Repetitivo</option>
              <option value="SAZONAL">Sazonal</option>
              <option value="ESPORADICO">Esporádico</option>
            </Select>
          </div>

          <div className="flex flex-col gap-1">
            <Label>Lead time (dias)</Label>
            <Input name="lead_time_dias" type="number" min={0} />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Estoque de segurança</Label>
            <Input name="estoque_seguranca" type="number" min={0} step="0.01" />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Ponto de pedido</Label>
            <Input name="ponto_pedido" type="number" min={0} step="0.01" />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Estoque máximo</Label>
            <Input name="estoque_maximo" type="number" min={0} step="0.01" />
          </div>

          <div className="md:col-span-4">
            <Button type="submit" disabled={salvando}>
              {salvando ? "Salvando..." : "Criar SKU"}
            </Button>
          </div>
        </form>
      </Card>

      <Table headers={["Código", "Descrição", "Criticidade", "Lead time", "Est. Segurança", "Pto. Pedido", "Est. Máximo", "Status", ""]}>
        {skus.map((sku) => (
          <tr key={sku.id}>
            <td className="px-3 py-2 font-medium">{sku.codigo}</td>
            <td className="px-3 py-2 text-slate-400">{sku.descricao}</td>
            <td className="px-3 py-2 text-slate-400">{sku.criticidade_resultado ?? "—"}</td>
            <td className="px-3 py-2 text-slate-400">{sku.lead_time_dias ?? "—"}</td>
            <td className="px-3 py-2 text-slate-400">{sku.estoque_seguranca ?? "—"}</td>
            <td className="px-3 py-2 text-slate-400">{sku.ponto_pedido ?? "—"}</td>
            <td className="px-3 py-2 text-slate-400">{sku.estoque_maximo ?? "—"}</td>
            <td className="px-3 py-2">
              <Badge tone={sku.ativo ? "success" : "neutral"}>{sku.ativo ? "Ativo" : "Inativo"}</Badge>
            </td>
            <td className="px-3 py-2">
              <button onClick={() => toggleAtivo(sku)} className="text-xs text-sky-400 hover:underline">
                {sku.ativo ? "Inativar" : "Reativar"}
              </button>
            </td>
          </tr>
        ))}
      </Table>
    </div>
  );
}
