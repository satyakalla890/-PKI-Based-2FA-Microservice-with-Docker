import base64
import pyotp


def generate_totp_code(hex_seed: str) -> str:
   
    seed_bytes = bytes.fromhex(hex_seed)

    base32_seed = base64.b32encode(seed_bytes).decode()

    totp = pyotp.TOTP(base32_seed)

    code = totp.now()

    return code

def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    
    # 1. Convert hex seed to bytes
    seed_bytes = bytes.fromhex(hex_seed)

    # 2. Convert bytes to base32 encoding
    base32_seed = base64.b32encode(seed_bytes).decode()

    # 3. Create TOTP object
    totp = pyotp.TOTP(base32_seed)

    # 4. Verify with ± valid_window tolerance
    return totp.verify(code, valid_window=valid_window)

if __name__ == "__main__":
    test_hex_seed = "0123456789abcdef" * 4  # 64 chars exactly

    code = generate_totp_code(test_hex_seed)
    print("Generated Code:", code)

    result = verify_totp_code(test_hex_seed, code)
    print("Verification Result:", result)