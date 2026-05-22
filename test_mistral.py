import os
import requests

api_key = os.getenv("MISTRAL_API_KEY")
base_url = "https://api.mistral.ai/v1/chat/completions"
model = "mistral-large-2512"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
payload = {
    "model": model,
    "messages": [
        {"role": "user", "content": "olá, responda apenas 'ok'"}
    ],
    "max_tokens": 10
}

try:
    response = requests.post(base_url, headers=headers, json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
