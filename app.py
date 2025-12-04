import os
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization

from crypto_utils import decrypt_seed            # your existing function
from totp_utils import generate_totp_code, verify_totp_code

# Constants
DATA_DIR = "/data"
SEED_FILE = "/data/seed.txt"

PRIVATE_KEY_FILE = "student_private.pem"   # file committed to repo per spec

app = FastAPI(title="PKI 2FA Microservice")


def load_private_key():
    """Load the student private key (PEM) from file."""
    try:
        with open(PRIVATE_KEY_FILE, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    except FileNotFoundError:
        raise RuntimeError("Private key file missing")
    except Exception as e:
        raise RuntimeError(f"Failed to load private key: {e}")


# Ensure data dir exists on startup (useful when testing locally)
os.makedirs(DATA_DIR, exist_ok=True)



class DecryptRequest(BaseModel):
    encrypted_seed: str


class VerifyRequest(BaseModel):
    code: str


# ---------- Endpoint 1: POST /decrypt-seed ----------
@app.post("/decrypt-seed")
def decrypt_seed_api(req: DecryptRequest):
    """
    Accepts base64 encrypted seed, decrypts using student private key,
    validates it is 64-char hex, and saves to /data/seed.txt
    """
    try:
        private_key = load_private_key()
        hex_seed = decrypt_seed(req.encrypted_seed, private_key)  # raises on invalid
        # Persist seed
        with open(SEED_FILE, "w") as f:
            f.write(hex_seed)
        return {"status": "ok"}
    except Exception:
        # avoid leaking internals, follow spec: return HTTP 500 with {"error":"Decryption failed"}
        raise HTTPException(status_code=500, detail={"error": "Decryption failed"})


# ---------- Endpoint 2: GET /generate-2fa ----------
@app.get("/generate-2fa")
def generate_2fa():
    """
    Reads /data/seed.txt, generates TOTP and returns code + seconds remaining.
    """
    if not os.path.exists(SEED_FILE):
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})
    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()
        code = generate_totp_code(hex_seed)
        # remaining seconds in current 30s window
        valid_for = 30 - (int(time.time()) % 30)
        return {"code": code, "valid_for": valid_for}
    except Exception as e:
        # unexpected internal error
        raise HTTPException(status_code=500, detail={"error": "TOTP generation failed", "msg": str(e)})


# ---------- Endpoint 3: POST /verify-2fa ----------
@app.post("/verify-2fa")
def verify_2fa(req: VerifyRequest):
    """
    Verify provided code against stored seed with ±1 period tolerance.
    """
    if not req.code:
        raise HTTPException(status_code=400, detail={"error": "Missing code"})
    if not os.path.exists(SEED_FILE):
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})
    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()
        valid = verify_totp_code(hex_seed, req.code, valid_window=1)
        return {"valid": bool(valid)}
    except Exception as e:
        # internal error
        raise HTTPException(status_code=500, detail={"error": "Verification failed", "msg": str(e)})
