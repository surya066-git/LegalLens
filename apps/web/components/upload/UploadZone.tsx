"use client";

import React, { useRef, useState } from "react";
import { UploadCloud, FileText, AlertCircle } from "lucide-react";
import { Button } from "../ui/Button";
import { Spinner } from "../ui/Spinner";
import { cn } from "@/lib/utils";

interface UploadZoneProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
  isProcessing?: boolean;
  error: string | null;
}

export function UploadZone({ onUpload, isUploading, isProcessing, error }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf") {
        onUpload(file);
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onUpload(e.target.files[0]);
      e.target.value = "";
    }
  };

  return (
    <div className="mx-auto max-w-2xl w-full">
      <div 
        role="region"
        aria-label="Upload document dropzone"
        className={cn(
          "relative mt-8 flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-12 transition-all duration-200",
          isDragging 
            ? "border-brand-500 bg-brand-50" 
            : "border-surface-300 bg-white hover:border-brand-400 hover:bg-surface-50",
          isUploading && "pointer-events-none opacity-60"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          aria-label="File upload input"
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept="application/pdf"
          className="hidden"
          disabled={isUploading}
        />
        
        <div className="mb-4 rounded-full bg-brand-100 p-4 text-brand-600">
          {isUploading ? <Spinner size="lg" /> : <UploadCloud size={32} strokeWidth={1.5} />}
        </div>
        
        <h3 className="mb-2 text-xl font-semibold text-surface-900">
          {isUploading ? "Processing document..." : "Upload your agreement"}
        </h3>
        
        <p className="mb-6 text-center text-sm text-surface-500 max-w-sm">
          Drop a PDF here or click to browse. We'll automatically extract the text and identify key clauses.
        </p>

        {!isUploading && (
          <Button 
            type="button"
            onClick={() => fileInputRef.current?.click()}
            size="lg"
            className="rounded-full px-8"
          >
            Choose PDF
          </Button>
        )}
        
        <div className="mt-8 flex items-center gap-2 text-xs font-medium text-surface-400">
          <FileText size={14} />
          <span>PDF • Up to 10 MB</span>
        </div>
      </div>

      {error && (
        <div role="alert" className="mt-4 flex items-center gap-2 rounded-lg bg-error-50 p-4 text-sm text-error-700 border border-error-200">
          <AlertCircle size={16} className="shrink-0" />
          <p>{error}</p>
        </div>
      )}
    </div>
  );
}
