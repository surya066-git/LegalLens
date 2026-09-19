import React from "react";
import { Scale, HelpCircle, User } from "lucide-react";
import { Button } from "../ui/Button";

export function Header() {
  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-surface-200 bg-white px-6">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white shadow-sm">
          <Scale size={18} strokeWidth={2.5} />
        </div>
        <span className="text-lg font-bold tracking-tight text-surface-900">
          LegalLens AI
        </span>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" className="text-surface-500 hidden sm:inline-flex">
          <HelpCircle size={20} />
        </Button>
        <div className="h-8 w-8 rounded-full bg-surface-100 border border-surface-200 flex items-center justify-center text-surface-600 ml-2">
          <User size={18} />
        </div>
      </div>
    </header>
  );
}
