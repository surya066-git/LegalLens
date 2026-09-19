"use client";

import { useCallback, useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { QuestionPanel } from "@/components/chat/QuestionPanel";
import { LegalDisclaimer } from "@/components/disclaimer/LegalDisclaimer";
import { AppShell } from "@/components/layout/AppShell";
import { UploadZone } from "@/components/upload/UploadZone";
import { askQuestion, createDocument, getBackendHealth, processDocument } from "@/lib/api";
import type { QuestionResponse } from "@/lib/schemas";
import { ShieldCheck } from "lucide-react";
import { Toast } from "@/components/ui/Toast";

const DocumentPanel = dynamic(() => import("@/components/pdf-viewer/DocumentPanel"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center text-sm text-surface-400">
      Preparing document viewer...
    </div>
  ),
});

export default function Home() {
  const [error, setError] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<{title: string, description?: string, type: "success" | "error" | "info"} | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [filename, setFilename] = useState<string | null>(null);
  const [documentMessage, setDocumentMessage] = useState<string | null>(null);
  const [answer, setAnswer] = useState<QuestionResponse | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<string | null>(null);
  
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [activePage, setActivePage] = useState<number>(1);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isAsking, setIsAsking] = useState(false);

  useEffect(() => {
    getBackendHealth()
      .catch((requestError: Error) => {
        setError(requestError.message);
        setToastMessage({
          title: "Backend connection failed",
          description: "Cannot connect to LegalLens AI API",
          type: "error",
        });
      });
  }, []);

  const dismissToast = useCallback(() => {
    setToastMessage(null);
  }, []);

  const handleUpload = useCallback(async (file: File) => {
    if (file.type !== "application/pdf") {
      setError("Please select a valid PDF file.");
      setPdfFile(null);
      setIsUploading(false);
      setIsProcessing(false);
      return;
    }

    setError(null);
    setPdfFile(file);
    setFilename(file.name);
    setDocumentId(null);
    setDocumentMessage(null);
    setAnswer(null);
    setCurrentQuestion(null);
    setActivePage(1);
    setIsUploading(true);
    setIsProcessing(true);

    try {
      const response = await createDocument(file);
      setDocumentId(response.documentId);
      setFilename(response.originalFilename);

      const processed = await processDocument(response.documentId);
      setDocumentMessage(
        `${processed.message} Pages: ${processed.pageCount}. Clauses detected: ${processed.clauseCount}.`,
      );
      setToastMessage({
        title: "Document Analyzed",
        description: `Successfully extracted ${processed.pageCount} pages and ${processed.clauseCount} clauses.`,
        type: "success",
      });
    } catch (requestError) {
      const errMsg = requestError instanceof Error ? requestError.message : "Upload failed.";
      setError(errMsg);
      setDocumentId(null);
      setPdfFile(null);
      setFilename(null);
      setToastMessage({ title: "Upload Failed", description: errMsg, type: "error" });
    } finally {
      setIsUploading(false);
      setIsProcessing(false);
    }
  }, []);

  const handleClose = useCallback(() => {
    setDocumentId(null);
    setFilename(null);
    setDocumentMessage(null);
    setAnswer(null);
    setCurrentQuestion(null);
    setPdfFile(null);
    setIsProcessing(false);
    setIsUploading(false);
    setError(null);
    setActivePage(1);
  }, []);

  const handleAsk = useCallback(async (question: string, modelSelection: string = "gemini_auto") => {
    if (!documentId) {
      setToastMessage({
        title: "No document selected",
        description: "Please upload a document first.",
        type: "error",
      });
      return;
    }

    setIsAsking(true);
    setCurrentQuestion(question);
    
    try {
      const response = await askQuestion(documentId, question, modelSelection);
      setAnswer(response);
      setError(null);
    } catch (requestError) {
      const errMsg = requestError instanceof Error ? requestError.message : "Question request failed.";
      setError(errMsg);
      setToastMessage({ title: "AI Request Failed", description: errMsg, type: "error" });
      setAnswer(null);
    } finally {
      setIsAsking(false);
    }
  }, [documentId]);

  const handleCitationClick = useCallback((page: number) => {
    setActivePage(page);
  }, []);

  const workspaceOpen = Boolean(pdfFile);

  return (
    <AppShell>
      {toastMessage && (
        <Toast 
          title={toastMessage.title} 
          description={toastMessage.description} 
          type={toastMessage.type}
          onClose={dismissToast} 
        />
      )}
      
      {!workspaceOpen ? (
        <div className="flex min-h-full flex-col items-center pt-10 md:pt-16 pb-10">
          <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-brand-600 text-white shadow-elevated">
            <ShieldCheck size={40} strokeWidth={1.5} />
          </div>
          <h1 className="mb-4 text-4xl md:text-5xl font-bold tracking-tight text-surface-900 text-center">
            Understand your legal documents.<br/>
            <span className="text-brand-600">Verify every answer.</span>
          </h1>
          <p className="mb-12 max-w-2xl text-center text-lg text-surface-600">
            LegalLens AI extracts clauses from employment agreements and validates every answer with verified source evidence.
          </p>
          
          <UploadZone onUpload={handleUpload} isUploading={isUploading} error={error} />
          
          <div className="mt-auto pt-16">
            <LegalDisclaimer />
          </div>
        </div>
      ) : (
        <div className="flex w-full flex-col lg:flex-row gap-6 pb-4 lg:h-[calc(100vh-9rem)]">
          <div className="w-full lg:w-1/2 h-[65vh] lg:h-full flex flex-col rounded-xl border border-surface-200 shadow-subtle overflow-hidden bg-white">
            <DocumentPanel 
              filename={filename} 
              statusMessage={documentMessage} 
              pdfFile={pdfFile}
              activePage={activePage}
              onPageChange={setActivePage}
              isProcessing={isProcessing}
              onClose={handleClose}
            />
          </div>
          <div className="w-full lg:w-1/2 h-[65vh] lg:h-full flex flex-col rounded-xl border border-surface-200 shadow-subtle overflow-hidden bg-white">
            <QuestionPanel 
              answer={answer} 
              currentQuestion={currentQuestion}
              disabled={!documentId || isUploading || isProcessing} 
              isLoading={isAsking} 
              onAsk={handleAsk} 
              onCitationClick={handleCitationClick}
            />
          </div>
        </div>
      )}
    </AppShell>
  );
}
