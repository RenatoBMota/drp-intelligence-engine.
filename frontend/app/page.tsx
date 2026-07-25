const FASES = [
  { numero: 1, nome: "Fundação", status: "Em andamento" },
  { numero: 2, nome: "Forecast", status: "Planejada" },
  { numero: 3, nome: "Motor DRP Core (MVP)", status: "Planejada" },
  { numero: 4, nome: "Otimização e IA", status: "Planejada" },
  { numero: 5, nome: "Torre de Controle", status: "Planejada" },
];

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center gap-8 px-6 py-16">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">
          DRP Intelligence Engine
        </h1>
        <p className="mt-2 text-slate-400">
          Planejamento de distribuição, otimização de estoques e forecast em
          rede — CD ↔ Filiais.
        </p>
      </div>

      <ol className="flex flex-col gap-2">
        {FASES.map((fase) => (
          <li
            key={fase.numero}
            className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/50 px-4 py-3"
          >
            <span>
              Fase {fase.numero} — {fase.nome}
            </span>
            <span className="text-sm text-slate-400">{fase.status}</span>
          </li>
        ))}
      </ol>
    </main>
  );
}
