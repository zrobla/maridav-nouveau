from __future__ import annotations

from contextvars import ContextVar, Token
from typing import Optional

from django.http import HttpRequest


_REQUEST_CONTEXT: ContextVar[HttpRequest | None] = ContextVar("crm_request_context", default=None)


def set_current_request(request: HttpRequest) -> Token:
    return _REQUEST_CONTEXT.set(request)


def reset_current_request(token: Token) -> None:
    _REQUEST_CONTEXT.reset(token)


def get_current_request() -> Optional[HttpRequest]:
    return _REQUEST_CONTEXT.get()

