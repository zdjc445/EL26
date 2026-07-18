import { useQuery } from "@tanstack/react-query";

import { getLiveStatus } from "./api";

export function SystemStatusPage() {
  const status = useQuery({
    queryKey: ["system", "live"],
    queryFn: ({ signal }) => getLiveStatus(signal),
  });

  return (
    <main className="status-shell">
      <section className="status-card" aria-labelledby="product-name">
        <p className="eyebrow">学习与行动 Agent</p>
        <h1 id="product-name">Time</h1>
        <p className="summary">工程基础运行状态</p>
        {status.isPending && <p role="status">正在确认服务状态…</p>}
        {status.isError && <p role="alert">无法确认服务状态</p>}
        {status.data && (
          <div className="health" role="status">
            <span className="health-dot" aria-hidden="true" />
            <span>服务正常</span>
            <span className="version">API {status.data.version}</span>
          </div>
        )}
      </section>
    </main>
  );
}
