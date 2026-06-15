import { UploadedDocument } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export async function uploadPdf(file: File): Promise<UploadedDocument> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed with status ${response.status}`);
  }

  return response.json();
}
