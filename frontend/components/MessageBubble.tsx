"use client";

import { useState } from "react";
import { ChatMessage, UploadedDocument } from "@/lib/types";
import { ChevronDown, ChevronUp } from "lucide-react";

interface MessageBubbleProps {
  message: ChatMessage;
  uploadedDocs: UploadedDocument[];
}

function getFilename(documentId: string, uploadedDocs: UploadedDocument[]): string {
  const doc = uploadedDocs.find((d) => d.document_id === documentId);
  return doc ? doc.original_filename : "Unknown document";
}

function distanceToRelevance(distance: number): number {
  const relevance = (1 - distance / 2) * 100;
  return Math.max(0, Math.min(100, Math.round(relevance)));
}

export function MessageBubble({ message, uploadedDocs }: MessageBubbleProps) {
  const [isSourcesOpen, setIsSourcesOpen] = useState(false);

  const isUser = message.role === "user";
  const hasSources = message.sources && message.sources.length > 0;

  return (
    <div className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}>
      <div
        className={`rounded-lg px-3 py-2 max-w-[80%] text-sm ${
          isUser ? "bg-primary text-primary-foreground" : "bg-muted"
        }`}
      >
        {message.content}
      </div>

      {hasSources && (
        <div className="mt-1 max-w-[80%]">
          <button
            onClick={() => setIsSourcesOpen((prev) => !prev)}
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            {isSourcesOpen ? (
              <ChevronUp className="h-3 w-3" />
            ) : (
              <ChevronDown className="h-3 w-3" />
            )}
            {message.sources!.length} source{message.sources!.length !== 1 ? "s" : ""}
          </button>

          {isSourcesOpen && (
            <div className="mt-2 space-y-2">
              {message.sources!.map((source, index) => (
                <div
                  key={index}
                  className="border rounded-md p-2 text-xs bg-background"
                >
                  <div className="flex justify-between items-center mb-1 text-muted-foreground">
                    <span className="font-medium">
                      {getFilename(source.document_id, uploadedDocs)} — Page {source.page_number}
                    </span>
                    <span>{distanceToRelevance(source.distance)}% relevant</span>
                  </div>
                  <p className="text-foreground/80 line-clamp-3">{source.text}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
