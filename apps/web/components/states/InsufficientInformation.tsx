import React from "react";
import { SearchX, HelpCircle, ArrowRight } from "lucide-react";
import { Card } from "../ui/Card";

interface InsufficientInformationProps {
  lawyerQuestions: string[];
}

export function InsufficientInformation({ lawyerQuestions }: InsufficientInformationProps) {
  return (
    <Card className="overflow-hidden border-surface-200">
      <div className="flex flex-col items-center justify-center p-8 text-center bg-surface-50 border-b border-surface-100">
        <div className="h-12 w-12 rounded-full bg-white border border-surface-200 flex items-center justify-center text-surface-400 mb-4 shadow-subtle">
          <SearchX size={24} strokeWidth={1.5} />
        </div>
        <h4 className="text-lg font-semibold text-surface-900 mb-2">Information not found</h4>
        <p className="text-sm text-surface-600 max-w-sm">
          The uploaded agreement does not contain enough information to answer this question reliably. We did not find supporting evidence in the document.
        </p>
      </div>

      {lawyerQuestions && lawyerQuestions.length > 0 && (
        <div className="p-6 bg-white">
          <div className="flex items-center gap-2 text-sm font-semibold text-surface-900 mb-4">
            <HelpCircle size={16} className="text-surface-400" />
            Suggested next step
          </div>
          <p className="text-sm text-surface-600 mb-3">Ask a qualified lawyer about:</p>
          <ul className="space-y-2">
            {lawyerQuestions.map((q, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-surface-700 bg-surface-50 p-3 rounded-lg border border-surface-100">
                <ArrowRight size={14} className="text-brand-500 mt-0.5 shrink-0" />
                <span>{q}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  );
}
