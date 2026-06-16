import { SourceChunk } from "@/lib/types";
import { getSession } from "next-auth/react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

interface ChatApiResponse {
  answer: string;
  sources: SourceChunk[];
  session_id: string;
}

export async function sendChatMessage(
  question: string,
  documentIds: string[],
  sessionId: string | null
): Promise<ChatApiResponse> {
  const session = await getSession();

  if (!session || !(session as any).apiToken) {
    throw new Error("You must be signed in to chat.");
  }

  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${(session as any).apiToken}`,
    },
    body: JSON.stringify({
      question,
      document_ids: documentIds.length > 0 ? documentIds : null,
      top_k: 4,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    const message = errorBody?.detail || `Chat request failed with status ${response.status}`;
    throw new Error(message);
  }

  return response.json();
}


export async function streamChatMessage(
  question: string,
  documentIds: string[],
  sessionId: string | null,
  onToken: (token: string) => void,
  onSources: (sources: SourceChunk[]) => void,
  onSessionId: (sessionId: string) => void,
  onDone: () => void,
  onError: (message: string) => void,
): Promise<void> {
  const session = await getSession();

  if (!session || !(session as any).apiToken) {
    onError("You must be signed in to chat.");
    return;
  }

  const response = await fetch(`${API_BASE_URL}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${(session as any).apiToken}`,
    },
    body: JSON.stringify({
      question,
      document_ids: documentIds.length > 0 ? documentIds : null,
      top_k: 4,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    const message = errorBody?.detail || `Stream request failed with status ${response.status}`;
    onError(message);
    return;
  }

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;

      const dataStr = line.slice("data: ".length).trim();
      if (dataStr === "[DONE]") {
        onDone();
        return;
      }

      try {
        const event = JSON.parse(dataStr);

        if (event.type === "token") {
          onToken(event.token);
        } else if (event.type === "sources") {
          onSources(event.sources);
        } else if (event.type === "session_id") {
          onSessionId(event.session_id);
        } else if (event.type === "error") {
          onError(event.message);
          return;
        }
      } catch {
        // malformed JSON in stream — skip
      }
    }
  }
}
