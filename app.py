# app.py
from flask import Flask, render_template, request, jsonify
import json
import os
import logging
import requests
import certifi
from convert_csv_to_json import load_initiatives

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
initiatives_data = load_initiatives()
# DHL OpenAI-compatible endpoint config
DHL_API_URL = "https://apihub-sandbox.dhl.com/genai-test/openai/deployments/text-embedding-ada-002-2/embeddings?api-version=2023-05-15"
DHL_API_KEY = os.environ.get("OPENAI_API_KEY")  # Replace with actual key or keep secure

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

def generate_similarity_reason(user_input, initiative_description):
    user_keywords = set(user_input.lower().split())
    initiative_keywords = set(initiative_description.lower().split())
    overlap = user_keywords & initiative_keywords

    if overlap:
        return f"Matches keywords: {', '.join(list(overlap)[:5])}"
    else:
        return "General similarity in description context."

# Find similar initiatives using embeddings
def find_similar_initiatives(user_description, initiatives, max_results=5):
    user_embedding = get_embedding(user_description)

    results = []
    for initiative in initiatives:
        if not isinstance(initiative, dict):
            continue

        initiative_desc = initiative.get('description', '')
        if not initiative_desc:
            continue

        initiative_embedding = initiative.get("embedding")
        if not initiative_embedding:
            continue

        similarity = calculate_cosine_similarity(user_embedding, initiative_embedding)

        reason = generate_similarity_reason(user_description, initiative_desc)

        results.append({
            'title': initiative.get('title', 'No Title'),
            'owner': initiative.get('owner', 'Unknown'),
            'campfire_id': initiative.get('campfire_id', 'N/A'),
            'link': initiative.get('link', '#'),
            'maturity': initiative.get('maturity', 'Unknown'),
            'similarity': similarity,
            'reason': reason
        })

    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results[:max_results]


# Cosine similarity calculation
def calculate_cosine_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5

    if magnitude1 * magnitude2 == 0:
        return 0

    return dot_product / (magnitude1 * magnitude2)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    user_description = request.form.get('description', '')
    print("User input:", user_description)

    similar_initiatives = find_similar_initiatives(user_description, initiatives_data)

    print("Similar initiatives:", similar_initiatives)
    return jsonify(similar_initiatives)

#if __name__ == '__main__':
    #app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
