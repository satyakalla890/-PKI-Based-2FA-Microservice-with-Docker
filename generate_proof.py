import subprocess
import sys
import base64
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

# File paths (adjust if necessary)
STUDENT_PRIV_PATH = "student_private.pem"
INSTRUCTOR_PUB_PATH = "instructor_public.pem"

def get_latest_commit_hash():
    """Return latest commit hash as ASCII string (40 hex chars)."""
    try:
        out = subprocess.check_output(["git", "log", "-1", "--format=%H"], stderr=subprocess.STDOUT)
        commit_hash = out.decode("utf-8").strip()
        if len(commit_hash) != 40:
            raise ValueError(f"Unexpected commit hash length: {commit_hash!r}")
        return commit_hash
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"git command failed: {e.output.decode('utf-8', errors='replace')}") from e

def load_private_key(path: str):
    data = Path(path).read_bytes()
    return serialization.load_pem_private_key(data, password=None)

def load_public_key(path: str):
    data = Path(path).read_bytes()
    return serialization.load_pem_public_key(data)

def sign_message(message: str, private_key) -> bytes:
    """
    Sign ASCII message (commit hash) using RSA-PSS with SHA-256 and max salt.
    Returns raw signature bytes.
    """
    msg_bytes = message.encode("utf-8")
    signature = private_key.sign(
        msg_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt data using RSA-OAEP with SHA-256 and MGF1(SHA-256).
    Returns ciphertext bytes.
    """
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def main():
    try:
        commit_hash = get_latest_commit_hash()
    except Exception as e:
        print("ERROR: unable to get git commit hash:", e, file=sys.stderr)
        sys.exit(2)

    # Load keys
    try:
        priv = load_private_key(STUDENT_PRIV_PATH)
    except Exception as e:
        print(f"ERROR: failed to load private key '{STUDENT_PRIV_PATH}': {e}", file=sys.stderr)
        sys.exit(3)

    try:
        pub = load_public_key(INSTRUCTOR_PUB_PATH)
    except Exception as e:
        print(f"ERROR: failed to load instructor public key '{INSTRUCTOR_PUB_PATH}': {e}", file=sys.stderr)
        sys.exit(4)

    # Sign
    try:
        sig = sign_message(commit_hash, priv)
    except Exception as e:
        print("ERROR: signing failed:", e, file=sys.stderr)
        sys.exit(5)

    # Encrypt signature with instructor public key
    try:
        encrypted = encrypt_with_public_key(sig, pub)
    except Exception as e:
        print("ERROR: encryption failed:", e, file=sys.stderr)
        sys.exit(6)

    # Base64 encode ciphertext and print single-line string
    b64 = base64.b64encode(encrypted).decode("utf-8")

    print("Commit Hash:", commit_hash)
    print("Encrypted Signature (base64):")
    print(b64)
    
    print("\n--- One-line pair (copy for submission) ---")
    print(f"{commit_hash} {b64}")

if __name__ == "__main__":
    main()
