import os
import requests
from flask import Flask, request, jsonify
from llmproxy import generate

app = Flask(__name__)

# Retrieve API Key & Endpoint from environment variables
apiKey = os.environ.get("apiKey", "").strip()
endPoint = os.environ.get("endPoint", "").strip().strip('"')  # Strip accidental quotes

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
    - Processes user messages for recipes, nutrition info, and general advice.
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

    # Check if user requested a **recipe**
    if message.startswith("recipe"):
        ingredients = message.replace("recipe", "").strip().split(",")
        ingredients = [ingredient.strip() for ingredient in ingredients]
        response_text = get_recipe(ingredients)
    
    # Check if user requested **nutrition info**
    elif message.startswith("nutrition"):
        item = message.replace("nutrition", "").strip()
        response_text = get_nutrition_info(item)

    # Check if user requested **general nutrition advice**
    elif message.startswith("general"):
        query = message.replace("general", "").strip()
        response_text = get_general_nutrition_advice(query)

    # If input is unclear, guide user
    else:
        response_text = (
            "❓ I'm not sure what you're asking. Try:\n\n"
            "🔹 `recipe oats, banana` - Get a recipe using these ingredients\n"
            "🔹 `nutrition spinach` - Get nutrition facts about spinach\n"
            "🔹 `general healthy eating` - Get general nutrition advice\n\n"
            "How can I help?"
        )

    # Send response back
    print(f"Response to {user}: {response_text}")
    return jsonify({"text": response_text})

### **Chatbot Logic (Merged from chatbot.py)**
def get_recipe(ingredients):
    """
    Retrieves a recipe from uploaded cookbooks if available; otherwise, generates a new one.
    """
    system_instruction = """
    You are a helpful nutritionist and recipe creator.
    If relevant recipes exist in the uploaded cookbooks, retrieve them.
    If no relevant recipes are found, generate a creative recipe based on the given ingredients.
    """

    query = f"Find a recipe using these ingredients: {', '.join(ingredients)}"

    response = generate(
        model="4o-mini",
        system=system_instruction,
        query=query,
        temperature=0.7,
        lastk=0,
        session_id="nutrition-bot-session2",  
        rag_threshold=0.4,  
        rag_usage=True,
        rag_k=5  
    )

    return response.get("response", "No recipe found. Try different ingredients!")

def get_nutrition_info(item):
    """
    Retrieves detailed nutritional information, prioritizing document-based retrieval.
    """
    system_instruction = """
    You are a helpful nutritionist providing science-backed dietary advice.
    Always prioritize data from official nutritional guidelines if available.
    If no document contains relevant information, generate a response based on general nutrition knowledge.
    """

    query = f"Provide nutritional information for {item} based on scientific sources."

    response = generate(
        model="4o-mini",
        system=system_instruction,
        query=query,
        temperature=0.7,
        lastk=0,
        session_id="nutrition-bot-session2",
        rag_threshold=0.3,
        rag_usage=True,
        rag_k=10
    )

    return response.get("response", "No nutritional information found.")

def get_general_nutrition_advice(query):
    """
    Provides general nutrition advice with priority given to uploaded documents.
    """
    system_instruction = """
    You are a knowledgeable nutritionist providing science-backed dietary advice.
    Format the response as follows:
    - **Topic Name**
    - **Key Recommendations:** (formatted bullet points)
    - **Why This Matters:** (explanation with supporting facts)
    - **Practical Tips:** (simple steps for implementation)
    """

    response = generate(
        model="4o-mini",
        system=system_instruction,
        query=query,
        temperature=0.7,
        lastk=0,
        session_id="nutrition-bot-session2",
        rag_threshold=0.5,
        rag_usage=True,
        rag_k=5
    )

    return response.get("response", "No relevant advice found. Try rewording your question.")

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Not Found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
