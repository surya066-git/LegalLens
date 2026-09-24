"use client";

import { memo, useCallback, useState } from "react";
import { FileText, ChevronLeft, ChevronRight, ZoomIn, ZoomOut, Maximize2, X } from "lucide-react";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { Spinner } from "../ui/Spinner";
import { PdfPreview } from "./PdfPreview";

type DocumentPanelProps = {
  filename: string | null;
  statusMessage: string | null;
  pdfFile: File | null;
  activePage: number;
  onPageChange: (page: number) => void;
  isProcessing?: boolean;
  onClose?: () => void;
};

function DocumentPanel({
  filename,
  statusMessage,
  pdfFile,
  activePage,
  onPageChange,
  isProcessing,
  onClose,
}: DocumentPanelProps) {
  const [numPages, setNumPages] = useState<number>();
  const [scale, setScale] = useState<number>(1.0);

  const handleNumPages = useCallback((nextNumPages: number) => {
    setNumPages(nextNumPages);
  }, []);

  return (
    <section className="flex flex-1 flex-col w-full h-full relative">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-surface-200 bg-white px-4 py-3 shrink-0 relative z-10 gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-surface-100 text-surface-600">
            <FileText className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-surface-900 truncate max-w-[200px] md:max-w-[300px]">
              {filename ?? "No document"}
            </h2>
            <div className="flex items-center gap-2 mt-0.5">
              {isProcessing ? (
                <Badge variant="brand" className="text-[10px] uppercase py-0 leading-tight flex items-center gap-1">
                  <Spinner size="sm" className="h-3 w-3" /> Processing
                </Badge>
              ) : pdfFile ? (
                <Badge variant="success" className="text-[10px] uppercase py-0 leading-tight">
                  Analyzed
                </Badge>
              ) : null}
              {statusMessage ? (
                <span className="text-[10px] text-surface-500 truncate max-w-[220px]">{statusMessage}</span>
              ) : null}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {pdfFile && numPages && (
            <div className="flex items-center gap-2 bg-surface-50 p-1 rounded-lg border border-surface-200">
              <Button 
                aria-label="Previous page"
                variant="ghost" 
                size="icon" 
                onClick={() => onPageChange(Math.max(1, activePage - 1))}
                disabled={activePage <= 1}
                className="h-7 w-7 rounded-md"
              >
                <ChevronLeft size={16} />
              </Button>
              <span className="text-xs font-medium text-surface-600 min-w-[3rem] text-center" aria-label={`Page ${activePage} of ${numPages}`}>
                {activePage} / {numPages}
              </span>
              <Button 
                aria-label="Next page"
                variant="ghost" 
                size="icon" 
                onClick={() => onPageChange(Math.min(numPages, activePage + 1))}
                disabled={activePage >= numPages}
                className="h-7 w-7 rounded-md"
              >
                <ChevronRight size={16} />
              </Button>
              
              <div className="w-px h-4 bg-surface-300 mx-1"></div>
              
              <Button aria-label="Zoom out" variant="ghost" size="icon" onClick={() => setScale((current) => Math.max(0.5, current - 0.25))} className="h-7 w-7 rounded-md">
                <ZoomOut size={14} />
              </Button>
              <span className="text-xs font-medium text-surface-600 w-10 text-center" aria-label={`Zoom level ${Math.round(scale * 100)}%`}>{Math.round(scale * 100)}%</span>
              <Button aria-label="Zoom in" variant="ghost" size="icon" onClick={() => setScale((current) => Math.min(3.0, current + 0.25))} className="h-7 w-7 rounded-md">
                <ZoomIn size={14} />
              </Button>
              <Button aria-label="Fit to width" variant="ghost" size="icon" onClick={() => setScale(1.0)} className="h-7 w-7 rounded-md ml-1 text-surface-400 hover:text-surface-900" title="Fit to width">
                <Maximize2 size={14} />
              </Button>
            </div>
          )}
          {onClose && (
            <Button aria-label="Close document" variant="ghost" size="icon" onClick={onClose} className="h-8 w-8 text-surface-400 hover:text-error-600 hover:bg-error-50 rounded-lg ml-2" title="Close Document">
              <X size={18} />
            </Button>
          )}
        </div>
      </div>

      <div className="flex-1 bg-surface-100 overflow-auto flex flex-col relative p-4">
        {pdfFile ? (
          <div className="mx-auto bg-white shadow-md">
            <PdfPreview
              file={pdfFile}
              pageNumber={activePage}
              scale={scale}
              onNumPages={handleNumPages}
            />
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-surface-400">
            <FileText size={48} className="mb-4 text-surface-300" strokeWidth={1} />
            <p className="text-sm font-medium">Document preview will appear here</p>
          </div>
        )}
      </div>
    </section>
  );
}

export default memo(DocumentPanel);
