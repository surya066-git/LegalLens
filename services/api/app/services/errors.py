from fastapi import HTTPException


SAFE_CLIENT_MESSAGES = {
    "internal_error": "An unexpected error occurred. Please try again.",
    "llm_error": "The AI service is temporarily unavailable. Please try again.",
    "llm_timeout": "The AI service timed out. Please try a shorter question or try again.",
    "llm_parsing_error": "The AI returned an unusable response. Please try again.",
    "llm_empty": "The AI returned an empty response. Please try again.",
    "rate_limited": "Too many requests. Please wait a moment and try again.",
}


def raise_api_error(status_code: int, code: str, message: str) -> None:
    raise HTTPException(
        status_code=status_code,
        detail={
            "code": code,
            "message": message,
        },
    )


def public_error_message(code: str, fallback: str) -> str:
    return SAFE_CLIENT_MESSAGES.get(code, fallback)
