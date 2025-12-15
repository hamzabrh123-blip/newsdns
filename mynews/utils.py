import base64

SECRET = "uphalchal"   # koi bhi fixed string

def encode_id(num):
    raw = f"{num}:{SECRET}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")

def decode_id(code):
    padded = code + "=" * (-len(code) % 4)
    raw = base64.urlsafe_b64decode(padded.encode()).decode()
    num, secret = raw.split(":")
    if secret != SECRET:
        raise ValueError("Invalid code")
    return int(num)
