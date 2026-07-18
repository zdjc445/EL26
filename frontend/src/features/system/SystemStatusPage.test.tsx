import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../../app/App";
import { AppProviders } from "../../app/AppProviders";

const livePayload = {
  status: "ok",
  service: "time-api",
  version: "0.1.0",
  build_sha: "test-sha",
};

describe("SystemStatusPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows the product identity and confirmed API status", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify(livePayload), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    render(
      <AppProviders>
        <App />
      </AppProviders>,
    );

    expect(screen.getByRole("heading", { name: "Time" })).toBeInTheDocument();
    expect(await screen.findByText("服务正常")).toBeInTheDocument();
    expect(screen.getByText("API 0.1.0")).toBeInTheDocument();
    const fetchMock = vi.mocked(fetch);
    expect(fetchMock).toHaveBeenCalledOnce();
    const firstCall = fetchMock.mock.calls[0];
    expect(firstCall?.[0]).toBe("/api/v1/health/live");
    expect(firstCall?.[1]?.signal).toBeInstanceOf(AbortSignal);
  });

  it("does not claim health when the API request fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(null, { status: 503 })),
    );

    render(
      <AppProviders>
        <App />
      </AppProviders>,
    );

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "无法确认服务状态",
    );
    expect(screen.queryByText("服务正常")).not.toBeInTheDocument();
  });
});
