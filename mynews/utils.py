# mynews/utils.py
import base64

SECRET = "uphalchal"   # change mat karna

def encode_id(num: int) -> str:
    raw = f"{num}:{SECRET}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")

def decode_id(code: str) -> int:
    try:
        padded = code + "=" * (-len(code) % 4)
        raw = base64.urlsafe_b64decode(padded.encode()).decode()
        num, secret = raw.split(":")
        if secret != SECRET:
            raise ValueError
        return int(num)
    except Exception:
        raise ValueError("Invalid news")
