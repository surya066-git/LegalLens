import React from "react";
import { type QuestionResponse } from "@/lib/schemas";
import { CitationCard } from "../citations/CitationCard";
import { AmbiguityState } from "../states/AmbiguityState";
import { InsufficientInformation } from "../states/InsufficientInformation";
import { LegalDisclaimer } from "../disclaimer/LegalDisclaimer";
import { Sparkles } from "lucide-react";
import { Card } from "../ui/Card";

interface AnswerCardProps {
  question: string;
  answer: QuestionResponse;
  onCitationClick: (page: number) => void;
}

export function AnswerCard({ question, answer, onCitationClick }: AnswerCardProps) {
  if (answer.insufficientInformation) {
    return (
      <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
        <div className="border-b border-surface-200 pb-4">
          <h3 className="text-xl font-semibold text-surface-900">{question}</h3>
        </div>
        <InsufficientInformation lawyerQuestions={answer.lawyerQuestions} />
        <LegalDisclaimer />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-300">
      <div className="border-b border-surface-200 pb-4">
        <h3 className="text-xl font-semibold text-surface-900">{question}</h3>
      </div>

      <div className="space-y-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-brand-600 uppercase tracking-wider">
          <Sparkles size={16} />
          <span>AI Explanation</span>
        </div>
        <div className="text-surface-800 leading-relaxed text-base">
          {answer.answer}
        </div>
      </div>

      {answer.citations.length > 0 && (
        <div className="space-y-4 pt-4">
          <div className="text-sm font-semibold text-surface-500 uppercase tracking-wider">
            Evidence
          </div>
          <div className="grid gap-3">
            {answer.citations.map((citation, index) => (
              <CitationCard 
                key={index} 
                citation={citation} 
                onClick={() => citation.page && onCitationClick(citation.page)} 
              />
            ))}
          </div>
        </div>
      )}

      {answer.ambiguities.length > 0 && (
        <AmbiguityState 
          ambiguities={answer.ambiguities} 
          lawyerQuestions={answer.lawyerQuestions} 
        />
      )}

      <div className="pt-4">
        <LegalDisclaimer />
      </div>
    </div>
  );
}
