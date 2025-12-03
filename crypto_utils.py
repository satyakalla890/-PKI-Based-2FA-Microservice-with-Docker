import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
   
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    decrypted_seed = decrypted_bytes.decode("utf-8").strip()

    if len(decrypted_seed) != 64:
        raise ValueError("Invalid seed length: must be 64 characters")

    allowed_chars = "0123456789abcdef"
    for ch in decrypted_seed:
        if ch not in allowed_chars:
            raise ValueError("Invalid seed format: must contain only hex characters")

    return decrypted_seed
