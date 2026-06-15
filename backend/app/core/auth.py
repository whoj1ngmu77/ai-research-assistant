from fastapi import HTTPException, Request
from jose import jwt
from jose.exceptions import JWTError
from app.core.config import AUTH_SECRET


async def get_current_user(request: Request) -> dict:
    """
    FastAPI dependency: extracts and verifies the API token issued by
    the frontend's NextAuth instance. Returns the user's identity.

    Raises 401 if the token is missing, invalid, or expired.
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.removeprefix("Bearer ").strip()

    try:
        payload = jwt.decode(token, AUTH_SECRET, algorithms=["HS256"])
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing subject (sub) claim")

    return {"user_id": user_id, "email": user_id}
