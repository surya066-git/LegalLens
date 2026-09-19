export type HealthResponse = {
  status: "ok";
  appName: string;
  environment: string;
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
  answer: string;
  confidence: "low" | "medium" | "high";
  insufficientInformation: boolean;
  citations: Citation[];
  ambiguities: string[];
  lawyerQuestions: string[];
  disclaimer: string;
};
