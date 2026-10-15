export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

export async function api<T>(path: string, options: RequestInit = {}, csrf?: string): Promise<T> {
  const method = options.method ?? "GET";
  const headers = new Headers(options.headers);
  if (method !== "GET") {
    headers.set("Content-Type", "application/json");
    headers.set("X-FeedbackForm-Request", "1");
    if (csrf) headers.set("X-CSRF-Token", csrf);
  }
  const response = await fetch(`/api${path}`, {
    ...options, headers, signal: options.signal ?? AbortSignal.timeout(10_000),
    credentials: "same-origin", cache: "no-store",
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new ApiError(response.status,
      typeof payload?.detail === "string" ? payload.detail : "Check your input and try again.");
  }
  return response.status === 204 ? undefined as T : response.json();
}
