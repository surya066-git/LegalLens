import { NextResponse } from "next/server";

const DEFAULT_BACKEND_URL = "http://127.0.0.1:8000";

export function backendUrl(path: string): string {
  const baseUrl = (process.env.BACKEND_API_URL ?? DEFAULT_BACKEND_URL).replace(/\/$/, "");
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${baseUrl}${suffix}`;
}

export async function forwardJson(path: string, init?: RequestInit, timeoutMs = 60_000): Promise<NextResponse> {
  return forwardBackend(
    path,
    {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
    },
    timeoutMs,
  );
}

export async function forwardMultipart(path: string, formData: FormData): Promise<NextResponse> {
  return forwardBackend(path, { method: "POST", body: formData }, 90_000);
}

async function forwardBackend(path: string, init: RequestInit | undefined, timeoutMs: number): Promise<NextResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(backendUrl(path), {
      ...init,
      cache: "no-store",
      signal: controller.signal,
    });
    const body = await response.text();
    return new NextResponse(body, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("Content-Type") ?? "application/json",
      },
    });
  } catch (error) {
    const timedOut = error instanceof DOMException && error.name === "AbortError";
    return NextResponse.json(
      {
        detail: {
          code: timedOut ? "backend_timeout" : "backend_unavailable",
          message: timedOut
            ? "The document service timed out. Please try again."
            : "The document service is unavailable. Please try again shortly.",
        },
      },
      { status: timedOut ? 504 : 503 },
    );
  } finally {
    clearTimeout(timeoutId);
  }
}
