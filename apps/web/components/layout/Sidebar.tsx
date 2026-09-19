import React from "react";
import { FileText, LayoutDashboard, History, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarItemProps {
  icon: React.ElementType;
  label: string;
  active?: boolean;
}

function SidebarItem({ icon: Icon, label, active }: SidebarItemProps) {
  return (
    <button
      type="button"
      className={cn(
        "flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all",
        active
          ? "bg-brand-50 text-brand-700"
          : "text-surface-600 hover:bg-surface-100 hover:text-surface-900"
      )}
    >
      <Icon size={18} className={cn(active ? "text-brand-600" : "text-surface-400")} />
      {label}
    </button>
  );
}

export function Sidebar() {
  return (
    <aside className="hidden w-64 flex-col border-r border-surface-200 bg-white md:flex">
      <div className="flex flex-1 flex-col gap-1 p-4">
        {/* Only implemented routes/features are active.
            Others are shown to complete the SaaS look, but not clickable right now
            since there are no other pages. */}
        <SidebarItem icon={FileText} label="Workspace" active />
        
        {/* Unimplemented sections just for SaaS visual structure per instructions */}
        <div className="mt-4 px-3 text-xs font-semibold uppercase tracking-wider text-surface-400">
          Coming Soon
        </div>
        <SidebarItem icon={LayoutDashboard} label="Dashboard" />
        <SidebarItem icon={History} label="History" />
        <SidebarItem icon={Settings} label="Settings" />
      </div>
      
      <div className="border-t border-surface-200 p-4">
        <div className="rounded-lg bg-surface-50 p-4 text-xs text-surface-500">
          <p className="font-semibold text-surface-700 mb-1">LegalLens AI Beta</p>
          <p>Verify all AI answers independently.</p>
        </div>
      </div>
    </aside>
  );
}
