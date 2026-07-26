"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, Fornecedor } from "@/lib/api";
import { Button, Card, ErrorBanner, Input, Label, Table } from "@/components/ui";

export default function FornecedoresPanel() {
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);

  const carregar = () => api.fornecedores.list().then(setFornecedores).catch((e) => setErro(String(e)));

  useEffect(() => {
    carregar();
  }, []);

  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formEl = e.currentTarget; // capturado antes do await — depois disso a SyntheticEvent zera currentTarget
    setSalvando(true);
    setErro(null);
    const form = new FormData(formEl);
    try {
      await api.fornecedores.create({
        razao_social: String(form.get("razao_social")),
        nome_fantasia: String(form.get("nome_fantasia") || "") || null,
        cnpj: String(form.get("cnpj")),
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
      <p className="mb-4 text-sm text-slate-400">Cadastro básico de fornecedores.</p>
      {erro && <ErrorBanner message={erro} />}

      <Card className="mb-6">
        <form onSubmit={onSubmit} className="grid grid-cols-1 gap-3 md:grid-cols-3">
          <div className="flex flex-col gap-1">
            <Label>Razão social *</Label>
            <Input name="razao_social" required />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Nome fantasia</Label>
            <Input name="nome_fantasia" />
          </div>
          <div className="flex flex-col gap-1">
            <Label>CNPJ *</Label>
            <Input name="cnpj" required />
          </div>
          <div className="md:col-span-3">
            <Button type="submit" disabled={salvando}>
              {salvando ? "Salvando..." : "Criar fornecedor"}
            </Button>
          </div>
        </form>
      </Card>

      <Table headers={["Razão social", "Nome fantasia", "CNPJ"]}>
        {fornecedores.map((f) => (
          <tr key={f.id}>
            <td className="px-3 py-2">{f.razao_social}</td>
            <td className="px-3 py-2 text-slate-400">{f.nome_fantasia ?? "—"}</td>
            <td className="px-3 py-2 text-slate-400">{f.cnpj}</td>
          </tr>
        ))}
      </Table>
    </div>
  );
}
