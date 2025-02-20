import os
import requests
from flask import Flask, request, jsonify
from llmproxy import generate
from chatbot import process_chat_query  # Import chatbot logic

app = Flask(__name__)

# Read API config from environment variables
API_KEY = os.environ.get("apiKey", "").strip()
ENDPOINT = os.environ.get("endPoint", "").strip().strip('"')  # Ensure no extra quotes

if not API_KEY or not ENDPOINT:
    raise RuntimeError("API_KEY or ENDPOINT is missing! Ensure they are set correctly in Koyeb.")

@app.route("/", methods=["POST"])
def handle_rocket_chat():
    """
    This function will now handle ALL messages from Rocket Chat directly.
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

    print(f"RAW LLMProxy Response: {response}")

    # Ensure response is a dictionary before calling `.get()`
    if isinstance(response, dict):
        response_text = response.get("response", "I couldn't process your request.")
    else:
        response_text = "Error: LLMProxy returned an unexpected response."

    print(f"Response to {user}: {response_text}")

    return jsonify({"text": response_text})  # ✅ This return is inside the function

@app.errorhandler(404)
def page_not_found(e):
    return "Not Found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
