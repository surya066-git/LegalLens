export type HealthResponse = {
  status: "ok";
  appName: string;
  environment: string;
  storageMode?: string;
};

export type DocumentCreateResponse = {
  documentId: string;
  originalFilename: string;
  storedFilename: string;
  status: "uploaded";
  fileSizeBytes: number;
  pageCount: number;
  message: string;
};

export type ProcessDocumentResponse = {
  documentId: string;
  status: "uploaded" | "processing" | "processed" | "failed";
  pageCount: number;
  clauseCount: number;
  chunkCount: number;
  warnings: string[];
  message: string;
};

export type Citation = {
  page: number | null;
  clauseNumber: string | null;
  sourceText: string;
  chunkId: string | null;
};

export type QuestionResponse = {
  status?: string;
  answerType: "DIRECTLY_ANSWERED" | "PARTIALLY_ANSWERED" | "NOT_FOUND";
  answer: string;
  confidence: "low" | "medium" | "high";
  missingInformation: string[];
  citations: Citation[];
  ambiguities: string[];
  lawyerQuestions: string[];
  disclaimer: string;
};

export type ApiErrorBody = {
  error?: string;
  detail?: {
    code?: string;
    message?: string;
  };
};
