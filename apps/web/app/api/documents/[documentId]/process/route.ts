import { forwardJson } from "@/app/api/_lib/backend";

type RouteContext = {
  params: Promise<{
    documentId: string;
  }>;
};

export async function POST(_request: Request, context: RouteContext) {
  const { documentId } = await context.params;

  return forwardJson(`/documents/${encodeURIComponent(documentId)}/process`, {
    method: "POST",
  });
}

