"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { sendChatMessage } from "@/lib/api/chat";
import { getSessionMessages } from "@/lib/api/sessions";
import { ChatMessage, UploadedDocument } from "@/lib/types";
import { MessageBubble } from "@/components/MessageBubble";

interface ChatInterfaceProps {
  documentIds: string[];
  uploadedDocs: UploadedDocument[];
  sessionId: string | null;
  onSessionCreated: (sessionId: string) => void;
  onChatComplete: () => void;
}

export function ChatInterface({
  documentIds,
  uploadedDocs,
  sessionId,
  onSessionCreated,
  onChatComplete,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (sessionId) {
      loadHistory(sessionId);
    } else {
      setMessages([]);
    }
  }, [sessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function loadHistory(id: string) {
    setIsLoadingHistory(true);
    try {
      const history = await getSessionMessages(id);
      setMessages(history);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoadingHistory(false);
    }
  }

  async function handleSend() {
    const question = input.trim();
    if (!question || isLoading) return;

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setIsLoading(true);

    try {
      const result = await sendChatMessage(question, documentIds, sessionId);

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.answer, sources: result.sources },
      ]);

      if (!sessionId) {
        onSessionCreated(result.session_id);
      }

      onChatComplete();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Something went wrong. Please try again.";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: message },
      ]);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter") {
      handleSend();
    }
  }

  return (
    <div className="flex flex-col w-full max-w-2xl h-[500px] border rounded-lg">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {isLoadingHistory && (
          <p className="text-sm text-muted-foreground text-center mt-8">
            Loading conversation...
          </p>
        )}

        {!isLoadingHistory && messages.length === 0 && (
          <p className="text-sm text-muted-foreground text-center mt-8">
            Ask a question about your uploaded documents.
          </p>
        )}

        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} uploadedDocs={uploadedDocs} />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="rounded-lg px-3 py-2 bg-muted text-sm text-muted-foreground">
              Thinking...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="flex gap-2 p-3 border-t">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question..."
          disabled={isLoading}
        />
        <Button onClick={handleSend} disabled={isLoading || !input.trim()}>
          Send
        </Button>
      </div>
    </div>
  );
}
