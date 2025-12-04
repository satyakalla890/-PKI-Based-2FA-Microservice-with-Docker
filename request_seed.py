import requests

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def request_seed(student_id: str, github_repo_url: str, api_url: str):

    with open("student_public.pem", "r") as f:
        public_key_pem = f.read()   # keep BEGIN/END + newlines

    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_pem
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(api_url, json=payload, headers=headers, timeout=15)

    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")

    data = response.json()

    if "encrypted_seed" not in data:
        raise Exception(f"Invalid API response: {data}")

    encrypted_seed = data["encrypted_seed"]

    
    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)

    print("✅ Encrypted seed saved to encrypted_seed.txt successfully!")



if __name__ == "__main__":
    STUDENT_ID = "23MH1A05H4"
    GITHUB_REPO_URL = "https://github.com/satyakalla890/-PKI-Based-2FA-Microservice-with-Docker.git"

    request_seed(STUDENT_ID, GITHUB_REPO_URL, API_URL)
