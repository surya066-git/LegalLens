"use client";

import { memo, useCallback } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";
import { Spinner } from "../ui/Spinner";

const PDF_OPTIONS = Object.freeze({});

function ensurePdfWorker() {
  if (typeof window === "undefined") return;
  if (pdfjs.GlobalWorkerOptions.workerSrc) return;
  pdfjs.GlobalWorkerOptions.workerSrc = "/pdf.worker.min.mjs";
}

type PdfPreviewProps = {
  file: File;
  pageNumber: number;
  scale: number;
  onNumPages: (numPages: number) => void;
};

export const PdfPreview = memo(function PdfPreview({
  file,
  pageNumber,
  scale,
  onNumPages,
}: PdfPreviewProps) {
  ensurePdfWorker();

  const onLoadSuccess = useCallback(
    ({ numPages }: { numPages: number }) => {
      onNumPages(numPages);
    },
    [onNumPages],
  );

  return (
    <Document
      file={file}
      onLoadSuccess={onLoadSuccess}
      options={PDF_OPTIONS}
      loading={
        <div className="flex flex-col items-center justify-center p-12 text-surface-400 gap-3">
          <Spinner size="lg" />
          <span className="text-sm">Loading document...</span>
        </div>
      }
      error={<div className="p-8 text-center text-error-600 text-sm">Failed to load PDF.</div>}
    >
      <Page
        pageNumber={pageNumber}
        scale={scale}
        renderTextLayer={true}
        renderAnnotationLayer={true}
        loading={
          <div className="flex flex-col items-center justify-center p-12 text-surface-400 h-[600px]">
            <Spinner />
          </div>
        }
      />
    </Document>
  );
});
