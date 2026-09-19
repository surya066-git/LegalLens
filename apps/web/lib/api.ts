import type {
  DocumentCreateResponse,
  HealthResponse,
  ProcessDocumentResponse,
  QuestionResponse,
} from "@/lib/schemas";

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function getBackendHealth(): Promise<HealthResponse> {
  const response = await fetch("/api/health", {
    cache: "no-store",
  });

  return readJson<HealthResponse>(response);
}

export async function createDocument(file: File): Promise<DocumentCreateResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/api/documents", {
    method: "POST",
    body: formData,
  });

  return readJson<DocumentCreateResponse>(response);
}

export async function processDocument(documentId: string): Promise<ProcessDocumentResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 60000);
  
  try {
    const response = await fetch(`/api/documents/${documentId}/process`, {
      method: "POST",
      signal: controller.signal,
    });
    return await readJson<ProcessDocumentResponse>(response);
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function askQuestion(
  documentId: string,
  question: string,
  modelSelection: string = "gemini_auto"
): Promise<QuestionResponse> {
  const response = await fetch(`/api/documents/${documentId}/questions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question, model_selection: modelSelection }),
  });

  return readJson<QuestionResponse>(response);
}

