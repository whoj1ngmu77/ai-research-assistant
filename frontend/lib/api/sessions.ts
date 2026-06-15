import { ChatSessionSummary, ChatMessage } from "@/lib/types";
import { getSession } from "next-auth/react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

async function authHeaders(): Promise<HeadersInit> {
  const session = await getSession();

  if (!session || !(session as any).apiToken) {
    throw new Error("You must be signed in.");
  }

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${(session as any).apiToken}`,
  };
}

export async function listSessions(): Promise<ChatSessionSummary[]> {
  const headers = await authHeaders();

  const response = await fetch(`${API_BASE_URL}/sessions`, { headers });

  if (!response.ok) {
    throw new Error(`Failed to load sessions (status ${response.status})`);
  }

  return response.json();
}

export async function getSessionMessages(sessionId: string): Promise<ChatMessage[]> {
  const headers = await authHeaders();

  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/messages`, { headers });

  if (!response.ok) {
    throw new Error(`Failed to load messages (status ${response.status})`);
  }

  const data = await response.json();

  return data.map((m: any) => ({
    role: m.role,
    content: m.content,
    sources: m.sources ?? undefined,
  }));
}

export async function deleteSession(sessionId: string): Promise<void> {
  const headers = await authHeaders();

  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}`, {
    method: "DELETE",
    headers,
  });

  if (!response.ok) {
    throw new Error(`Failed to delete session (status ${response.status})`);
  }
}
