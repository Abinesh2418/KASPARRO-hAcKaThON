import requests
import json

url = "http://100.127.36.42:11434/api/generate"
payload = {
    "model": "deepseek-r1:14b",
    "prompt": "hello",
    "stream": False
}

print(f"Testing Ollama endpoint: {url}")
print(f"Model: {payload['model']}")
print("-" * 40)

try:
    response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    print("Status: OK")
    print(f"Response: {data.get('response', '').encode('ascii', errors='replace').decode()}")
    print(f"Done: {data.get('done', '')}")
except requests.exceptions.ConnectionError:
    print("ERROR: Could not connect to the server. Is Ollama running?")
except requests.exceptions.Timeout:
    print("ERROR: Request timed out after 60 seconds.")
except requests.exceptions.HTTPError as e:
    print(f"ERROR: HTTP {e.response.status_code} - {e.response.text}")
except Exception as e:
    print(f"ERROR: {e}")
