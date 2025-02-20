import os
import requests
from flask import Flask, request, jsonify
from llmproxy import generate

app = Flask(__name__)

# Load API Key and Endpoint from environment variables
API_KEY = os.environ.get("apiKey", "").strip()
ENDPOINT = os.environ.get("endPoint", "").strip()

if not API_KEY or not ENDPOINT:
    raise RuntimeError("API_KEY or ENDPOINT is missing! Ensure they are set correctly in Koyeb.")

@app.route('/', methods=['POST'])
def hello_world():
    return jsonify({"text": 'Hello from Koyeb - you reached the main page!'})

@app.route('/query', methods=['POST'])
def main():
    data = request.get_json() 

    # Extract relevant information
    user = data.get("user_name", "Unknown")
    message = data.get("text", "")

    print(data)

    # Ignore bot messages
    if data.get("bot") or not message:
        return jsonify({"status": "ignored"})

    print(f"Message from {user}: {message}")

    # Generate a response using LLMProxy with API key and endpoint
    response = generate(
        model='4o-mini',
        system='answer my question and add keywords',
        query=message,
        temperature=0.0,
        lastk=0,
        session_id='GenericSession',
        api_key=API_KEY,  # Ensure API key is passed
        endpoint=ENDPOINT  # Ensure endpoint is passed
    )

    # Check if response is valid
    if isinstance(response, dict):
        response_text = response.get("response", "I couldn't process your request.")
    else:
        response_text = f"Error: Unexpected response format: {response}"

    # Send response back
    print(response_text)

    return jsonify({"text": response_text})

@app.errorhandler(404)
def page_not_found(e):
    return "Not Found", 404

if __name__ == "__main__":
    app.run()
