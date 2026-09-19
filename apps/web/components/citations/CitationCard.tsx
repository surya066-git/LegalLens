import React from "react";
import { CheckCircle2, ChevronRight } from "lucide-react";
import { type Citation } from "@/lib/schemas";
import { Card } from "../ui/Card";

interface CitationCardProps {
  citation: Citation;
  onClick: () => void;
}

export function CitationCard({ citation, onClick }: CitationCardProps) {
  return (
    <Card className="overflow-hidden border-surface-200 transition-all hover:border-surface-300 hover:shadow-elevated">
      <div className="flex items-center justify-between border-b border-surface-100 bg-surface-50 px-4 py-2.5">
        <div className="flex items-center gap-3 text-xs font-medium uppercase tracking-wider text-surface-500">
          {citation.page && <span>Page {citation.page}</span>}
          {citation.page && citation.clauseNumber && <span className="text-surface-300">•</span>}
          {citation.clauseNumber && <span>Clause {citation.clauseNumber}</span>}
        </div>
        <div className="flex items-center gap-1.5 rounded-full bg-success-50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-success-700 border border-success-200">
          <CheckCircle2 size={12} />
          Verified
        </div>
      </div>
      
      <div className="p-4">
        <p className="font-serif text-surface-700 leading-relaxed italic border-l-2 border-surface-200 pl-4">
          "{citation.sourceText}"
        </p>
      </div>

      <button 
        type="button"
        onClick={onClick}
        className="flex w-full items-center justify-center gap-1 border-t border-surface-100 bg-surface-50 py-2.5 text-xs font-medium text-surface-600 hover:bg-surface-100 hover:text-surface-900 transition-colors"
      >
        View page <ChevronRight size={14} />
      </button>
    </Card>
  );
}
