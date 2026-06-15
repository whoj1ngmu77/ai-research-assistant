"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import { PdfUploader } from "@/components/PdfUploader";
import { ChatInterface } from "@/components/ChatInterface";
import { AuthButton } from "@/components/AuthButton";
import { Sidebar } from "@/components/Sidebar";
import { UploadedDocument } from "@/lib/types";

export default function Home() {
  const { status } = useSession();
  const [uploadedDocs, setUploadedDocs] = useState<UploadedDocument[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [sidebarRefreshKey, setSidebarRefreshKey] = useState(0);

  function handleUploadSuccess(doc: UploadedDocument) {
    setUploadedDocs((prev) => [...prev, doc]);
  }

  function handleSelectSession(sessionId: string) {
    setActiveSessionId(sessionId);
  }

  function handleNewChat() {
    setActiveSessionId(null);
  }

  function handleSessionCreated(sessionId: string) {
    setActiveSessionId(sessionId);
    setSidebarRefreshKey((prev) => prev + 1);
  }

  const documentIds = uploadedDocs.map((doc) => doc.document_id);

  if (status === "unauthenticated") {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-8 gap-6">
        <div className="absolute top-4 right-4">
          <AuthButton />
        </div>
        <div className="text-center">
          <h1 className="text-3xl font-bold">AI Research Assistant</h1>
          <p className="mt-2 text-muted-foreground">
            Sign in to upload documents and start chatting.
          </p>
        </div>
      </main>
    );
  }

  if (status === "loading") {
    return null;
  }

  return (
    <div className="flex h-screen">
      <Sidebar
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        refreshKey={sidebarRefreshKey}
      />

      <main className="flex-1 flex flex-col items-center p-8 gap-6 overflow-y-auto">
        <div className="absolute top-4 right-4">
          <AuthButton />
        </div>

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
          </div>
        )}

        <ChatInterface
          documentIds={documentIds}
          uploadedDocs={uploadedDocs}
          sessionId={activeSessionId}
          onSessionCreated={handleSessionCreated}
        />
      </main>
    </div>
  );
}
