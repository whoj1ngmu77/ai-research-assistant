import { SourceChunk } from "@/lib/types";
import { getSession } from "next-auth/react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

interface ChatApiResponse {
  answer: string;
  sources: SourceChunk[];
}

export async function sendChatMessage(
  question: string,
  documentIds: string[]
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
    }),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    const message = errorBody?.detail || `Chat request failed with status ${response.status}`;
    throw new Error(message);
  }

  return response.json();
}
