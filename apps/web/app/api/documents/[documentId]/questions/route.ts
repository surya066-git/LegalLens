import { forwardJson } from "@/app/api/_lib/backend";

type RouteContext = {
  params: Promise<{
    documentId: string;
  }>;
};

export async function POST(request: Request, context: RouteContext) {
  const { documentId } = await context.params;
  const body = await request.text();

  return forwardJson(`/documents/${encodeURIComponent(documentId)}/questions`, {
    method: "POST",
    body,
  });
}

