import csv
import json
import requests
import certifi
import os

# DHL OpenAI-compatible endpoint config
DHL_API_URL = "https://apihub-sandbox.dhl.com/genai-test/openai/deployments/text-embedding-ada-002-2/embeddings?api-version=2023-05-15"
DHL_API_KEY = os.environ.get("OPENAI_API_KEY")  # Make sure to set this

# Get embedding from DHL endpoint
def get_embedding(text):
    headers = {
        "Content-Type": "application/json",
        "api-key": DHL_API_KEY
    }
    payload = {
        "input": [text]
    }

    response = requests.post(DHL_API_URL, headers=headers, json=payload, verify=certifi.where())
    response.raise_for_status()
    embedding = response.json()["data"][0]["embedding"]
    return embedding

def load_initiatives():
    try:
        with open('initiatives.json', 'r') as file:
            data = json.load(file)
            initiatives = data.get('initiatives', [])
            print("Loaded initiatives:", initiatives)  # Debug log
            return initiatives
    except Exception as e:
        logger.error(f"Error loading initiatives: {e}")
        return []

# Load the CSV file and convert it to JSON with embeddings
def load_csv_to_json(csv_file='CampfireData.csv'):
    initiatives = []
    with open(csv_file, 'r', encoding='utf-8-sig') as file:  # Use 'utf-8-sig' encoding to handle BOM
        reader = csv.DictReader(file)
        print("CSV Headers:", reader.fieldnames)
        for row in reader:
            initiative = {
                "title": row.get("Title", "").strip(),
                "owner": row.get("Owner", "").strip(),
                "campfire_id": row.get("Campfire_Id", "").strip(),
                "description": row.get("Description", "").strip(),
                "link": row.get("Link", "").strip(),
                "maturity": row.get("Maturity Level", "").strip(),
                "embedding": get_embedding(row["Description"])  # Get embedding for description
            }
            initiatives.append(initiative)
    return initiatives

# Save the data to initiatives.json
def save_to_json(initiatives, json_file='initiatives.json'):
    data = {"initiatives": initiatives}
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Saved {len(initiatives)} initiatives to {json_file}")

# Run the process to load CSV, get embeddings, and save the JSON
def convert_csv_to_json():
    initiatives = load_csv_to_json()  # Load CSV and generate embeddings
    save_to_json(initiatives)  # Save initiatives as JSON

# Run the conversion
#convert_csv_to_json()
