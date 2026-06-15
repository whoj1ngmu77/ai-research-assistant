import { getSession } from "next-auth/react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export interface AnalyticsData {
  documents_uploaded: number;
  questions_asked: number;
  avg_response_time_ms: number | null;
  total_chunks_stored: number;
}

export async function getAnalytics(): Promise<AnalyticsData> {
  const session = await getSession();

  if (!session || !(session as any).apiToken) {
    throw new Error("You must be signed in.");
  }

  const response = await fetch(`${API_BASE_URL}/analytics`, {
    headers: {
      Authorization: `Bearer ${(session as any).apiToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to load analytics (status ${response.status})`);
  }

  return response.json();
}
