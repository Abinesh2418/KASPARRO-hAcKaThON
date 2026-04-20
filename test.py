import requests

url = "http://100.127.36.42:11434/api/generate"

payload = {
    "model": "deepseek-r1:32b",
    "prompt": "hello",
    "stream": False
}

response = requests.post(url, json=payload)

print(response.json()["response"])