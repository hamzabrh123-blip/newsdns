# mynews/utils.py
import base64

SECRET = "uphalchal"

def encode_id(news_id: int) -> str:
    raw = f"news:{news_id}:{SECRET}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")

def decode_id(code: str) -> int:
    try:
        padded = code + "=" * (-len(code) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode()).decode()
        prefix, news_id, secret = decoded.split(":")
        if prefix != "news" or secret != SECRET:
            raise ValueError
        return int(news_id)
    except Exception:
        raise ValueError("Invalid code")
