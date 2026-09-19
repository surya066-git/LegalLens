import React, { useEffect } from "react";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface ToastProps {
  title: string;
  description?: string;
  type?: "success" | "error" | "info";
  onClose: () => void;
}

export function Toast({ title, description, type = "info", onClose }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 5000);
    return () => clearTimeout(timer);
    // Parent re-renders should not reset this timer.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const icons = {
    success: <CheckCircle2 className="h-5 w-5 text-success-600" />,
    error: <AlertCircle className="h-5 w-5 text-error-600" />,
    info: <Info className="h-5 w-5 text-brand-600" />
  };

  const bgStyles = {
    success: "bg-success-50 border-success-200",
    error: "bg-error-50 border-error-200",
    info: "bg-brand-50 border-brand-200"
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-in slide-in-from-bottom-5 fade-in duration-300">
      <div className={cn(
        "flex w-full max-w-sm items-start gap-3 rounded-xl border p-4 shadow-float",
        bgStyles[type]
      )}>
        <div className="shrink-0 mt-0.5">{icons[type]}</div>
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-surface-900">{title}</h4>
          {description && <p className="mt-1 text-sm text-surface-600 leading-relaxed">{description}</p>}
        </div>
        <button 
          type="button"
          onClick={onClose}
          className="rounded-lg p-1 text-surface-400 hover:bg-surface-100 hover:text-surface-900 focus:outline-none focus:ring-2 focus:ring-surface-900/10 transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
