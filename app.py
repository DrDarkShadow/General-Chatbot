from flask import Flask, render_template, request, jsonify, session
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Configure Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2023-09-01-preview"
)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")  # Set a secret key for session management

# Function to interact with OpenAI
def chat_with_bot(user_input):
    try:
        # Retrieve conversation history from session
        conversation_history = session.get('conversation_history', [])
        
        # Add the new user input to the conversation history
        conversation_history.append({"role": "user", "content": user_input})
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who gives short precise and meaningful answers. and also try to give the answers in one line or paragraph only"}
            ] + conversation_history,
            temperature=0.7,
            max_tokens=800
        )
        
        # Add the bot's response to the conversation history
        bot_response = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": bot_response})
        
        # Save the updated conversation history back to the session
        session['conversation_history'] = conversation_history
        
        return bot_response
    except Exception as e:
        return f"Error: {str(e)}"

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint for chatbot
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    bot_response = chat_with_bot(user_input)
    return jsonify({"response": bot_response})

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
