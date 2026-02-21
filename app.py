# Import necessary modules for the web framework, API requests, and JSON responses
from flask import Flask, request, jsonify
# Import CORS so your frontend (React, Vue, HTML/JS) can securely talk to this API
from flask_cors import CORS
# Import the official Google Generative AI SDK
import google.generativeai as genai
# Import os to securely access environment variables from the operating system
import os
# Import load_dotenv to read the .env file locally during development
from dotenv import load_dotenv

# Execute the function to load environment variables into the script
load_dotenv()

# ← PASTE YOUR GOOGLE AI STUDIO KEY IN .env FILE
# ← YOUR API KEY IN .env
# Securely retrieve the key from memory so it's never hardcoded in your source code
api_key = os.getenv("GOOGLE_API_KEY")

# Configure the Gemini SDK using the loaded API key
genai.configure(api_key=api_key)

# Initialize the Flask application instance
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing on the app instance
CORS(app)

# Define the AI's core personality instructions
SYSTEM_PROMPT = """You are a highly capable, premium personal assistant.
Your tone is warm, helpful, smart, and deeply conversational.
Always provide well-structured, easy-to-read responses.
Sound natural and human-like—never robotic or overly formal.
Always remember the context of the conversation, address the user warmly, and be proactive in your assistance."""

# Initialize the Gemini model with the designated model version and personality
# ← CHANGE MODEL HERE IF NEEDED
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=SYSTEM_PROMPT
)

# Define the API endpoint that listens for POST requests at the '/chat' URL path
@app.route('/chat', methods=['POST'])
def chat_endpoint():
    # Start a try-except block to gracefully catch and handle any crashes
    try:
        # Parse the incoming JSON payload sent by the frontend
        data = request.get_json()

        # If no JSON data was provided, return a 400 Bad Request error
        if not data:
            return jsonify({"error": "Invalid or missing JSON payload", "status": "error"}), 400

        # Extract the user's current message from the payload
        user_message = data.get("message")

        # Validate that the message exists and is not just empty spaces
        if not user_message or not user_message.strip():
            return jsonify({"error": "Message cannot be empty", "status": "error"}), 400

        # Extract the conversation history array, defaulting to an empty list if none provided
        raw_history = data.get("history", [])

        # Create an empty list to store the history converted into Gemini's specific format
        formatted_history = []

        # Loop over every past message sent by the frontend
        for msg in raw_history:
            # Safely grab the role and content from the dictionary
            role = msg.get("role", "")
            content = msg.get("content", "")

            # If either value is missing, skip this specific message to avoid crashing
            if not role or not content:
                continue

            # Map the frontend's "assistant" role strictly to Gemini's "model" role
            if role == "assistant":
                gemini_role = "model"
            # Map the frontend's "user" role strictly to Gemini's "user" role
            elif role == "user":
                gemini_role = "user"
            # If a completely unrecognized role is passed, skip it
            else:
                continue

            # Append the properly mapped dictionary into our formatted list
            formatted_history.append({
                "role": gemini_role,
                "parts": [content]
            })

        # Spin up a new active chat session, injecting the newly formatted historical context
        chat_session = model.start_chat(history=formatted_history)

        # Transmit the user's newest message to the AI and wait for it to generate a reply
        response = chat_session.send_message(user_message)

        # Extract just the text string from the AI's full response object
        ai_reply = response.text

        # Package the AI's reply and a success status into a JSON dictionary and send it back
        return jsonify({
            "reply": ai_reply,
            "status": "success"
        }), 200

    # If absolutely anything goes wrong above, catch the exception here
    except Exception as e:
        # Print the exact error out to the server console so you can debug it locally
        print(f"Backend Error: {str(e)}")
        # Send a safe, clean JSON error message back to the frontend with a 500 status code
        return jsonify({
            "error": "The assistant encountered an internal server error.", 
            "status": "error"
        }), 500

# Standard Python check to ensure the server only runs if this file is executed directly
if __name__ == '__main__':
    # Boot up the development server on port 5000, allowing connections from any IP
    app.run(host='0.0.0.0', port=5000, debug=True)
                                    
