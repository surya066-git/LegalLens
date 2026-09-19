"use client";

import React, { memo, useCallback, useState } from "react";
import { Send, Sparkles } from "lucide-react";
import { type QuestionResponse } from "@/lib/schemas";
import { Button } from "../ui/Button";
import { Spinner } from "../ui/Spinner";
import { AnswerCard } from "./AnswerCard";

interface QuestionPanelProps {
  onAsk: (question: string) => Promise<void>;
  isLoading: boolean;
  answer: QuestionResponse | null;
  currentQuestion: string | null;
  onCitationClick: (page: number) => void;
  disabled?: boolean;
}

const SUGGESTED_QUESTIONS = [
  "What is the notice period?",
  "What happens during probation?",
  "Are there termination conditions?",
  "Does the agreement restrict joining competitors?",
] as const;

const SuggestedQuestions = memo(function SuggestedQuestions({
  disabled,
  onSelect,
}: {
  disabled?: boolean;
  onSelect: (question: string) => void;
}) {
  return (
    <div className="grid w-full max-w-md gap-3">
      {SUGGESTED_QUESTIONS.map((question) => (
        <button
          key={question}
          type="button"
          onClick={() => onSelect(question)}
          disabled={disabled}
          className="flex w-full items-center justify-between rounded-xl border border-surface-200 bg-white p-4 text-left text-sm font-medium text-surface-700 shadow-subtle transition-all hover:border-brand-300 hover:shadow-md disabled:pointer-events-none disabled:opacity-50 group"
        >
          {question}
          <div className="rounded-full bg-surface-100 p-1.5 text-surface-400 group-hover:bg-brand-50 group-hover:text-brand-600 transition-colors">
            <Send size={14} />
          </div>
        </button>
      ))}
    </div>
  );
});

export const QuestionPanel = memo(function QuestionPanel({
  onAsk,
  isLoading,
  answer,
  currentQuestion,
  onCitationClick,
  disabled,
}: QuestionPanelProps) {
  const [inputValue, setInputValue] = useState("");

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading && !disabled) {
      onAsk(inputValue.trim());
      setInputValue("");
    }
  }, [disabled, inputValue, isLoading, onAsk]);

  const handleSuggestClick = useCallback((question: string) => {
    if (!isLoading && !disabled) {
      onAsk(question);
    }
  }, [disabled, isLoading, onAsk]);

  const showSuggestions = !answer && !isLoading && !currentQuestion;

  return (
    <div className="flex h-full flex-col bg-white">
      <div className="flex-1 overflow-y-auto p-6 scroll-smooth">
        {showSuggestions ? (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 shadow-subtle border border-brand-100">
              <Sparkles size={32} strokeWidth={1.5} />
            </div>
            <h2 className="mb-2 text-2xl font-semibold tracking-tight text-surface-900">
              Ask about this agreement
            </h2>
            <p className="mb-8 max-w-md text-surface-500">
              Select a suggested question below, or ask anything about the document. The AI will extract relevant clauses and verify them against the text.
            </p>
            <SuggestedQuestions disabled={disabled} onSelect={handleSuggestClick} />
          </div>
        ) : isLoading ? (
          <div className="space-y-6">
            <div className="border-b border-surface-200 pb-4">
              <h3 className="text-xl font-semibold text-surface-900">{currentQuestion}</h3>
            </div>
            <div className="flex flex-col items-center justify-center py-20 text-surface-400">
              <Spinner size="lg" className="mb-4 text-brand-600" />
              <p className="text-sm font-medium animate-pulse">Analyzing document structure...</p>
            </div>
          </div>
        ) : answer && currentQuestion ? (
          <AnswerCard 
            question={currentQuestion} 
            answer={answer} 
            onCitationClick={onCitationClick} 
          />
        ) : null}
      </div>

      <div className="shrink-0 border-t border-surface-200 bg-white p-4">
        <div className="relative mx-auto max-w-3xl">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                handleSubmit(e as unknown as React.FormEvent);
              }
            }}
            disabled={disabled || isLoading}
            placeholder={disabled ? "Upload a document to start asking questions..." : "Ask a question about the document..."}
            className="w-full rounded-2xl border border-surface-200 bg-surface-50 py-3.5 pl-5 pr-14 text-sm text-surface-900 placeholder:text-surface-400 focus:border-brand-500 focus:bg-white focus:outline-none focus:ring-4 focus:ring-brand-500/10 transition-all disabled:opacity-60"
          />
          <div className="absolute right-2 top-2">
            <Button
              type="button"
              onClick={handleSubmit}
              size="icon"
              disabled={!inputValue.trim() || disabled || isLoading}
              className="h-10 w-10 rounded-xl bg-brand-600 text-white shadow-sm hover:bg-brand-700 disabled:bg-surface-200 disabled:text-surface-400"
            >
              <Send size={18} className={isLoading ? "animate-pulse" : ""} />
            </Button>
          </div>
        </div>
        <p className="mt-3 text-center text-[11px] text-surface-400 font-medium tracking-wide">
          LegalLens AI can make mistakes. Verify important information against the source document.
        </p>
      </div>
    </div>
  );
});
