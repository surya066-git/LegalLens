import { forwardMultipart } from "@/app/api/_lib/backend";

export async function POST(request: Request) {
  const formData = await request.formData();

  return forwardMultipart("/documents", formData);
}
