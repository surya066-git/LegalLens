import { FileText } from "lucide-react";
import type { Citation } from "@/lib/schemas";

type CitationListProps = {
  citations: Citation[];
  onCitationClick: (page: number) => void;
};

export function CitationList({ citations, onCitationClick }: CitationListProps) {
  if (citations.length === 0) {
    return (
      <p className="rounded-md border border-line bg-paper p-3 text-sm text-ink/70">
        No citations available yet.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {citations.map((citation, index) => (
        <article className="rounded-md border border-line bg-paper p-3" key={`${citation.chunkId}-${index}`}>
          <div className="flex items-center justify-between mb-2">
            <div className="text-xs font-semibold uppercase text-ink/60">
              Page {citation.page ?? "unknown"} · Clause {citation.clauseNumber ?? "not present"}
            </div>
            {citation.page != null && (
              <button 
                type="button"
                onClick={() => onCitationClick(citation.page!)}
                className="inline-flex items-center gap-1 text-xs font-medium text-teal hover:text-teal/80 bg-teal/10 px-2 py-1 rounded"
              >
                <FileText className="w-3 h-3" />
                View Page
              </button>
            )}
          </div>
          <p className="text-sm">{citation.sourceText}</p>
        </article>
      ))}
    </div>
  );
}

