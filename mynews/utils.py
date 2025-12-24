# mynews/utils.py
import base64

SECRET = "uphalchal"


def encode_id(news_id: int) -> str:
    raw = f"news:{news_id}:{SECRET}"
    encoded = base64.urlsafe_b64encode(raw.encode()).decode()
    return encoded.rstrip("=")


def decode_id(code):
    try:
        decoded = base64.urlsafe_b64decode(code.encode()).decode()
        parts = decoded.split(":")

        if len(parts) != 3:
            raise ValueError("Invalid code format")

        prefix, news_id, secret = parts
        return int(news_id)


    except Exception:
        # fallback: agar direct ID aa jaye
        if code.isdigit():
            return int(code)
        raise ValueError("Invalid code")
