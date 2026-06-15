export interface UploadedDocument {
  document_id: string;
  original_filename: string;
  chunks_created: number;
}

export interface SourceChunk {
  text: string;
  page_number: number;
  document_id: string;
  distance: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: SourceChunk[];
}
