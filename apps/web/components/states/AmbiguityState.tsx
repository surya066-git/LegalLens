import React from "react";
import { AlertTriangle, ArrowRight, HelpCircle } from "lucide-react";
import { Card } from "../ui/Card";

interface AmbiguityStateProps {
  ambiguities: string[];
  lawyerQuestions?: string[];
}

export function AmbiguityState({ ambiguities, lawyerQuestions }: AmbiguityStateProps) {
  if (!ambiguities.length) return null;

  return (
    <Card className="overflow-hidden border-warning-200 bg-warning-50/30">
      <div className="flex items-center gap-2 border-b border-warning-100 bg-warning-50 px-4 py-3">
        <AlertTriangle size={16} className="text-warning-600" />
        <h4 className="text-sm font-semibold text-warning-900">Potential ambiguity</h4>
      </div>
      
      <div className="p-4 space-y-4">
        {ambiguities.map((ambiguity, index) => (
          <p key={index} className="text-sm text-surface-700 leading-relaxed">
            {ambiguity}
          </p>
        ))}

        {lawyerQuestions && lawyerQuestions.length > 0 && (
          <div className="mt-4 pt-4 border-t border-warning-100">
            <div className="flex items-center gap-2 text-sm font-semibold text-surface-900 mb-3">
              <HelpCircle size={14} className="text-surface-500" />
              Questions for a lawyer
            </div>
            <ul className="space-y-2">
              {lawyerQuestions.map((q, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-surface-700">
                  <ArrowRight size={14} className="text-warning-500 mt-0.5 shrink-0" />
                  <span>{q}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Card>
  );
}
