from google import genai
from app.core.config import GEMINI_API_KEY
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.genai.errors import ServerError

client = genai.Client(api_key=GEMINI_API_KEY)

GENERATION_MODEL = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """You are an AI research assistant. You answer questions based ONLY on the provided context from the user's uploaded documents.

Rules:
- Answer using only the information in the CONTEXT section below.
- If the context does not contain enough information to answer, say "I don't have enough information in the uploaded documents to answer that."
- Do not use any outside knowledge.
- Be concise and direct.
- If relevant, mention which part of the document the information comes from."""


def build_prompt(question: str, chunks: list[dict]) -> str:
    context_blocks = []
    for i, chunk in enumerate(chunks):
        context_blocks.append(
            f"[Excerpt {i+1} - Page {chunk['page_number']}]\n{chunk['text']}"
        )

    context_text = "\n\n".join(context_blocks)

    prompt = f"""CONTEXT:
{context_text}

QUESTION:
{question}"""

    return prompt


@retry(
    retry=retry_if_exception_type(ServerError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
def _call_gemini(prompt: str):
    return client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "temperature": 0.2,
        },
    )


def generate_answer(question: str, chunks: list[dict]) -> str:
    prompt = build_prompt(question, chunks)
    response = _call_gemini(prompt)
    return response.text
