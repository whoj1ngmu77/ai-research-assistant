"use client";

import { useState } from "react";
import { PdfUploader } from "@/components/PdfUploader";
import { ChatInterface } from "@/components/ChatInterface";
import { UploadedDocument } from "@/lib/types";

export default function Home() {
  const [uploadedDocs, setUploadedDocs] = useState<UploadedDocument[]>([]);

  function handleUploadSuccess(doc: UploadedDocument) {
    setUploadedDocs((prev) => [...prev, doc]);
  }

  const documentIds = uploadedDocs.map((doc) => doc.document_id);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 gap-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold">AI Research Assistant</h1>
        <p className="mt-2 text-muted-foreground">
          Upload a PDF and ask questions about it.
        </p>
      </div>

      <PdfUploader onUploadSuccess={handleUploadSuccess} />

      {uploadedDocs.length > 0 && (
        <div className="w-full max-w-2xl">
          <h2 className="text-sm font-medium mb-2">Uploaded documents:</h2>
          <ul className="space-y-1 mb-4">
            {uploadedDocs.map((doc) => (
              <li
                key={doc.document_id}
                className="text-sm border rounded px-3 py-2"
              >
                {doc.original_filename} — {doc.chunks_created} chunks
              </li>
            ))}
          </ul>

          <ChatInterface documentIds={documentIds} uploadedDocs={uploadedDocs} />
        </div>
      )}
    </main>
  );
}
