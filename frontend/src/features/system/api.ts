export interface LiveStatus {
  status: "ok";
  service: "time-api";
  version: string;
  build_sha: string;
}

function isLiveStatus(value: unknown): value is LiveStatus {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const candidate = value as Record<string, unknown>;
  return (
    candidate.status === "ok" &&
    candidate.service === "time-api" &&
    typeof candidate.version === "string" &&
    typeof candidate.build_sha === "string"
  );
}

export async function getLiveStatus(signal?: AbortSignal): Promise<LiveStatus> {
  const requestInit: RequestInit = signal === undefined ? {} : { signal };
  const response = await fetch("/api/v1/health/live", requestInit);
  if (!response.ok) {
    throw new Error(`Live status request failed with HTTP ${response.status}`);
  }
  const payload: unknown = await response.json();
  if (!isLiveStatus(payload)) {
    throw new Error("Live status response did not match the public contract");
  }
  return payload;
}
