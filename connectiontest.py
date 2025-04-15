import requests
import certifi
import socket
import os

# Check SSL cert (optional)
print("CA cert file:", certifi.where())

# Test connectivity to DHL sandbox
try:
    socket.create_connection(("apihub-sandbox.dhl.com", 443), timeout=10)
    print("✅ Can connect to DHL sandbox domain")
except Exception as e:
    print(f"❌ Cannot connect to DHL sandbox domain: {e}")

# DHL API parameters
API_KEY = os.environ.get("OPENAI_API_KEY")  # Replace with your actual key
DEPLOYMENT_NAME = "text-embedding-ada-002-2"  # Confirm this is the right deployment
API_VERSION = "2023-05-15"
URL = f"https://apihub-sandbox.dhl.com/genai-test/openai/deployments/{DEPLOYMENT_NAME}/embeddings?api-version={API_VERSION}"

headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY
}

payload = {
    "input": ["Test connection"]  # Embedding input must be a list
}

try:
    response = requests.post(URL, headers=headers, json=payload, verify=certifi.where())
    response.raise_for_status()
    result = response.json()
    print("✅ Connection successful!")
    print("Embedding result:", result)
except requests.exceptions.HTTPError as errh:
    print("❌ HTTP Error:", errh.response.text)
except requests.exceptions.RequestException as err:
    print("❌ Request Error:", err)
