import { NextResponse } from "next/server";

const DEFAULT_BACKEND_URL = "http://127.0.0.1:8000";

export function backendUrl(path: string): string {
  const baseUrl = process.env.BACKEND_API_URL ?? DEFAULT_BACKEND_URL;
  return new URL(path, baseUrl).toString();
}

export async function forwardJson(
  path: string,
  init?: RequestInit,
): Promise<NextResponse> {
  return forwardBackend(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
}

export async function forwardMultipart(path: string, formData: FormData): Promise<NextResponse> {
  return forwardBackend(path, {
    method: "POST",
    body: formData,
  });
}

async function forwardBackend(
  path: string,
  init?: RequestInit,
): Promise<NextResponse> {
  try {
    const response = await fetch(backendUrl(path), {
      ...init,
      cache: "no-store",
    });

    const body = await response.text();

    return new NextResponse(body, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("Content-Type") ?? "application/json",
      },
    });
  } catch {
    return NextResponse.json(
      {
        error: "Backend API is unavailable or misconfigured. Please check your network connection or try again later.",
      },
      { status: 503 },
    );
  }
}
