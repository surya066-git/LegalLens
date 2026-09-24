import type {
  DocumentCreateResponse,
  HealthResponse,
  ProcessDocumentResponse,
  QuestionResponse,
} from "@/lib/schemas";

const PROCESS_TIMEOUT_MS = 90_000;
const QUESTION_TIMEOUT_MS = 60_000;
const DEFAULT_TIMEOUT_MS = 20_000;

export function parseApiErrorMessage(payload: string, status: number): string {
  try {
    const body = JSON.parse(payload) as {
      error?: string;
      detail?: { message?: string; code?: string } | string;
    };
    if (typeof body.error === "string" && body.error.trim()) {
      return body.error;
    }
    if (typeof body.detail === "string" && body.detail.trim()) {
      return body.detail;
    }
    if (body.detail && typeof body.detail === "object" && body.detail.message) {
      return body.detail.message;
    }
  } catch {
    if (payload.trim()) {
      return payload.slice(0, 400);
    }
  }
  return `Request failed with status ${status}`;
}

async function readJson<T>(response: Response): Promise<T> {
  const payload = await response.text();
  if (!response.ok) {
    throw new Error(parseApiErrorMessage(payload, response.status));
  }
  if (!payload) {
    throw new Error("The server returned an empty response.");
  }
  return JSON.parse(payload) as T;
}

async function fetchWithTimeout(input: string, init: RequestInit, timeoutMs: number): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(input, { ...init, signal: controller.signal, cache: "no-store" });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("The request timed out. Please try again.");
    }
    throw new Error("Network request failed. Check your connection and try again.");
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function getBackendHealth(): Promise<HealthResponse> {
  const response = await fetchWithTimeout("/api/health", { method: "GET" }, DEFAULT_TIMEOUT_MS);
  return readJson<HealthResponse>(response);
}

export async function createDocument(file: File): Promise<DocumentCreateResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetchWithTimeout("/api/documents", { method: "POST", body: formData }, PROCESS_TIMEOUT_MS);
  return readJson<DocumentCreateResponse>(response);
}

export async function processDocument(documentId: string): Promise<ProcessDocumentResponse> {
  const response = await fetchWithTimeout(
    `/api/documents/${encodeURIComponent(documentId)}/process`,
    { method: "POST" },
    PROCESS_TIMEOUT_MS,
  );
  return readJson<ProcessDocumentResponse>(response);
}

export async function askQuestion(
  documentId: string,
  question: string,
  modelSelection: string = "gemini_auto",
): Promise<QuestionResponse> {
  const response = await fetchWithTimeout(
    `/api/documents/${encodeURIComponent(documentId)}/questions`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, model_selection: modelSelection }),
    },
    QUESTION_TIMEOUT_MS,
  );
  return readJson<QuestionResponse>(response);
}

export async function deleteDocument(documentId: string): Promise<void> {
  const response = await fetchWithTimeout(
    `/api/documents/${encodeURIComponent(documentId)}`,
    { method: "DELETE" },
    DEFAULT_TIMEOUT_MS,
  );
  if (response.status === 404) {
    return;
  }
  await readJson<{ status: string }>(response);
}
