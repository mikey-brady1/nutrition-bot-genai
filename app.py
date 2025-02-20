import os
import requests
from flask import Flask, request, jsonify
from llmproxy import generate
from chatbot import process_chat_query  # Import chatbot logic

app = Flask(__name__)

# Read API config from environment variables
API_KEY = os.environ.get("apiKey", "").strip()
ENDPOINT = os.environ.get("endPoint", "").strip()

if not API_KEY or not ENDPOINT:
    raise RuntimeError("API_KEY or ENDPOINT is missing! Ensure they are set correctly in Koyeb.")

@app.route('/', methods=['POST'])
def hello_world():
    return jsonify({"text": 'Hello from Koyeb - you reached the main page!'})

@app.route('/query', methods=['POST'])
def handle_rocket_chat():
    """
    Handles queries from Rocket Chat webhook.
    """
    data = request.get_json()

    # Extract message details
    user = data.get("user_name", "Unknown")
    message = data.get("text", "")

    print(f"Incoming request: {data}")

    # Ignore bot messages
    if data.get("bot") or not message:
        return jsonify({"status": "ignored"})

    print(f"Message from {user}: {message}")

    # Generate a response using LLMProxy
    response = generate(
        model="4o-mini",
        system="Answer the question concisely and provide relevant details.",
        query=message,
        temperature=0.7,
        lastk=0,
        session_id="GenericSession"
    )

    response_text = response.get("response", "I couldn't process your request.")

    print(f"Response to {user}: {response_text}")

    return jsonify({"text": response_text})


@app.route('/chat', methods=['POST'])
def chat():
    """
    Handles user queries related to nutrition and recipes.
    Routes request to chatbot.py for processing.
    """
    data = request.get_json()
    return process_chat_query(data)  # Call chatbot logic

@app.errorhandler(404)
def page_not_found(e):
    return "Not Found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
