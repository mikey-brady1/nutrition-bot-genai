import os
import requests
from flask import Flask, request, jsonify
from llmproxy import generate
from chatbot import process_chat_query  # Import chatbot logic

app = Flask(__name__)

# Retrieve API Key & Endpoint from environment variables
apiKey = os.environ.get("apiKey", "").strip()
endPoint = os.environ.get("endPoint", "").strip().strip('"')  # Strip to remove accidental quotes

# Debugging Logs
print(f"Loaded API Key: {apiKey}")  
print(f"Loaded Endpoint: {endPoint}")  

if not apiKey or not endPoint:
    raise RuntimeError("API_KEY or ENDPOINT is missing! Ensure they are set correctly in Koyeb.")

@app.route('/query', methods=['POST'])
def main():
    """
    Handles all queries from Rocket.Chat.
    - Guides users on how to interact with the chatbot.
    - Processes user messages via chatbot.py.
    """
    data = request.get_json() 

    # Extract relevant information
    user = data.get("user_name", "Unknown")
    message = data.get("text", "").strip().lower()

    print(f"Incoming request: {data}")

    # Ignore bot messages
    if data.get("bot") or not message:
        return jsonify({"status": "ignored"})

    print(f"Message from {user}: {message}")

    # **Initial User Guidance**
    if message in ["hello", "hi", "hey"]:
        response_text = (
            "👋 Hello! Welcome to the Nutrition Chatbot! Here's how to use me:\n\n"
            "1️⃣ *Get a Recipe:* Type `recipe` followed by ingredients (e.g., `recipe oats, banana`)\n"
            "2️⃣ *Get Nutrition Info:* Type `nutrition` followed by a food name (e.g., `nutrition spinach`)\n"
            "3️⃣ *Get General Nutrition Advice:* Type `general` followed by a topic (e.g., `general healthy eating`)\n\n"
            "💡 How can I assist you today?"
        )
        return jsonify({"text": response_text})

    # Send request to chatbot logic
    return process_chat_query(data)

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Not Found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
