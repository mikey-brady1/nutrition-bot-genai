import os
from flask import Flask, request, jsonify, render_template
from llmproxy import generate

app = Flask(__name__)

# Read API config from environment variables
endPoint = os.environ.get("endPoint")
apiKey = os.environ.get("apiKey")

if not API_KEY or not ENDPOINT:
    raise RuntimeError("API_KEY or ENDPOINT is missing! Set them as environment variables.")

def get_recipe(ingredients):
    """
    Retrieves a recipe from uploaded cookbooks if available; otherwise, generates a new one.
    """
    system_instruction = """
    You are a helpful nutritionist and recipe creator.
    If relevant recipes exist in the uploaded cookbooks, retrieve them.
    If no relevant recipes are found, generate a creative recipe based on the given ingredients.

    Format the response as follows:
    - **Recipe Name**
    - **Ingredients:** (formatted list)
    - **Instructions:** (numbered list)
    - **Summary:** (short paragraph explaining the benefits of this recipe)
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

    return format_recipe_response(response.get("response", "No recipe found. Try different ingredients!"))


def get_nutrition_info(item):
    """
    Retrieves detailed nutritional information, prioritizing document-based retrieval.
    """
    system_instruction = """
    You are a helpful nutritionist providing science-backed dietary advice.
    Always prioritize data from official nutritional guidelines if available.
    If no document contains relevant information, generate a response based on general nutrition knowledge.

    Format the response as follows:
    - **Nutrient Breakdown for [Item]**
    - **Key Nutrients:** (formatted list with values)
    - **Health Benefits:** (formatted list)
    - **Dietary Considerations:** (potential concerns or modifications)
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

    return format_nutrition_response(response.get("response", "No nutritional information found."))


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

    return format_nutrition_advice_response(response.get("response", "No relevant advice found. Try rewording your question."))


def format_recipe_response(text):
    """
    Ensures proper formatting for recipes.
    """
    formatted_text = text.replace("###", "<h3>").replace("**", "<strong>").replace("\n", "<br>")
    formatted_text = formatted_text.replace("Ingredients:", "<h4>Ingredients:</h4>")
    formatted_text = formatted_text.replace("Instructions:", "<h4>Instructions:</h4>")
    formatted_text = formatted_text.replace("Summary:", "<h4>Summary:</h4>")
    return formatted_text


def format_nutrition_response(text):
    """
    Ensures proper formatting for nutritional information.
    """
    formatted_text = text.replace("###", "<h3>").replace("**", "<strong>").replace("\n", "<br>")
    formatted_text = formatted_text.replace("Key Nutrients:", "<h4>Key Nutrients:</h4>")
    formatted_text = formatted_text.replace("Health Benefits:", "<h4>Health Benefits:</h4>")
    formatted_text = formatted_text.replace("Dietary Considerations:", "<h4>Dietary Considerations:</h4>")
    return formatted_text


def format_nutrition_advice_response(text):
    """
    Ensures proper formatting for general nutrition advice.
    """
    formatted_text = text.replace("###", "<h3>").replace("**", "<strong>").replace("\n", "<br>")
    formatted_text = formatted_text.replace("Key Recommendations:", "<h4>Key Recommendations:</h4>")
    formatted_text = formatted_text.replace("Why This Matters:", "<h4>Why This Matters:</h4>")
    formatted_text = formatted_text.replace("Practical Tips:", "<h4>Practical Tips:</h4>")
    return formatted_text


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    Handles user queries by routing them to the appropriate function.
    """
    data = request.get_json()
    user_input = data.get("message")
    query_type = data.get("queryType")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    if query_type == "recipe":
        ingredients = user_input.split(",")
        response = get_recipe(ingredients)
    elif query_type == "nutrition":
        response = get_nutrition_info(user_input)
    elif query_type == "general":
        response = get_general_nutrition_advice(user_input)
    else:
        response = "Invalid query type."

    return jsonify({"response": response, "queryType": query_type})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
