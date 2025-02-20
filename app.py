import os
import requests
from flask import Flask, request, jsonify
from llmproxy import generate

app = Flask(__name__)

# Retrieve API Key & Endpoint from environment variables
apiKey = os.environ.get("apiKey", "").strip()
endPoint = os.environ.get("endPoint", "").strip().strip('"')  # Strip to remove accidental quotes

# Debug
print(f"Loaded API Key: {apiKey}")  
print(f"Loaded Endpoint: {endPoint}")  

if not apiKey or not endPoint:
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

    print(f"Incoming request: {data}")

    # Ignore bot messages
    if data.get("bot") or not message:
        return jsonify({"status": "ignored"})

    print(f"Message from {user}: {message}")

    # Debug 2: Print API Key and Endpoint inside function
    print(f"API Key: {apiKey}")  # Masked API Key
    print(f"Endpoint: {endPoint}")

    # Generate a response using LLMProxy
    response = generate(
        model='4o-mini',
        system='answer my question and add keywords',
        query=message,
        temperature=0.0,
        lastk=0,
        session_id='GenericSession'
    )

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
