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
  if (answer.answerType === "NOT_FOUND") {
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
          {answer.answerType === "PARTIALLY_ANSWERED" && (
            <span className="ml-2 rounded-full bg-warning-100 px-2 py-0.5 text-xs text-warning-700 font-medium">
              Partial Information
            </span>
          )}
        </div>
        <div className="text-surface-800 leading-relaxed text-base">
          {answer.answer}
        </div>
      </div>

      {answer.missingInformation && answer.missingInformation.length > 0 && (
        <div className="space-y-3 pt-2">
          <div className="text-sm font-semibold text-warning-600 uppercase tracking-wider">
            Missing from Document
          </div>
          <ul className="list-disc pl-5 text-sm text-surface-600 space-y-1">
            {answer.missingInformation.map((info, idx) => (
              <li key={idx}>{info}</li>
            ))}
          </ul>
        </div>
      )}

      {answer.citations && answer.citations.length > 0 && (
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

      {answer.ambiguities && answer.ambiguities.length > 0 && (
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
