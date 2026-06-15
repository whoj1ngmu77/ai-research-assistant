import { UploadedDocument } from "@/lib/types";
import { getSession } from "next-auth/react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export async function uploadPdf(file: File): Promise<UploadedDocument> {
  const session = await getSession();

  if (!session || !(session as any).apiToken) {
    throw new Error("You must be signed in to upload.");
  }

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${(session as any).apiToken}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    const message = errorBody?.detail || `Upload failed with status ${response.status}`;
    throw new Error(message);
  }

  return response.json();
}
