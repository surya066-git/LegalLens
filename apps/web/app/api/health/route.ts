import { forwardJson } from "@/app/api/_lib/backend";

export const dynamic = "force-dynamic";

export async function GET() {
  return forwardJson("/health");
}

