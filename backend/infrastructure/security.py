"""Configurações de segurança e validação de input."""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware simples para rate limiting (exemplo)."""

    async def dispatch(self, request: Request, call_next):
        # Placeholder para lógica real de rate limit
        return await call_next(request)


def validate_pdf_content(content: bytes) -> bool:
    """Valida se o conteúdo é um PDF válido."""
    return content.startswith(b"%PDF-")
