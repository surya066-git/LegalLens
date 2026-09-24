import { forwardJson } from "@/app/api/_lib/backend";

type RouteContext = {
  params: Promise<{
    documentId: string;
  }>;
};

export async function GET(_request: Request, context: RouteContext) {
  const { documentId } = await context.params;
  return forwardJson(`/documents/${encodeURIComponent(documentId)}`, { method: "GET" }, 20_000);
}

export async function DELETE(_request: Request, context: RouteContext) {
  const { documentId } = await context.params;
  return forwardJson(`/documents/${encodeURIComponent(documentId)}`, { method: "DELETE" }, 20_000);
}
