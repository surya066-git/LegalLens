import React from "react";
import { Info } from "lucide-react";

export function LegalDisclaimer() {
  return (
    <div className="flex items-start gap-2 rounded-lg bg-surface-100 p-3 text-xs text-surface-500 border border-surface-200 mt-6">
      <Info size={14} className="shrink-0 mt-0.5 text-surface-400" />
      <p>
        <strong className="font-medium text-surface-700">Legal information only — not legal advice.</strong>{" "}
        Consider consulting a qualified lawyer for advice about your specific situation.
      </p>
    </div>
  );
}
