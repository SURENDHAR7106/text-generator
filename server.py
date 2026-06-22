import os
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# Load .env using the absolute path of THIS file's directory
# This ensures the .env is found even when Flask's reloader changes the cwd
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

# Initialize Flask app — serve static files from the 'static' folder
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)  # Allow cross-origin requests from the browser

# Model and system prompt constants
MODEL_NAME = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = "You are a professional AI writing assistant that generates clear, meaningful, and grammatically correct text."

def get_groq_client():
    """
    Initializes and returns the Groq API client.
    Raises a ValueError if the GROQ_API_KEY is missing or is still the placeholder.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key.strip() == "your_groq_api_key_here":
        raise ValueError(
            "Groq API Key is not configured. Please set GROQ_API_KEY in your .env file."
        )
    return Groq(api_key=api_key)


def call_groq(system_msg, user_msg, temperature, max_tokens):
    """
    Sends a message to the Groq API and returns the response text.
    Handles authentication, network, and general API errors.
    """
    client = get_groq_client()
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return completion.choices[0].message.content


# ────────────────────────────────────────────────
# Serve the main index.html
# ────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ────────────────────────────────────────────────
# Route: Generate text
# ────────────────────────────────────────────────
@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = (data.get("prompt") or "").strip()
    style = data.get("style", "Professional")
    temperature = float(data.get("temperature", 0.7))
    max_tokens = int(data.get("max_tokens", 250))

    if not prompt:
        return jsonify({"error": "Prompt cannot be empty."}), 400

    user_msg = f"Generate a {style} response for the following request:\n{prompt}"

    try:
        result = call_groq(SYSTEM_PROMPT, user_msg, temperature, max_tokens)
        return jsonify({"result": result})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 401
    except Exception as e:
        err = str(e)
        if "401" in err or "Unauthorized" in err:
            return jsonify({"error": "Invalid Groq API key. Please check your .env file."}), 401
        return jsonify({"error": f"API Error: {err}"}), 500


# ────────────────────────────────────────────────
# Route: Text modification (Summarize, Expand, Rewrite, Continue)
# ────────────────────────────────────────────────
@app.route("/api/modify", methods=["POST"])
def modify():
    data = request.get_json()
    action = data.get("action", "")
    text = (data.get("text") or "").strip()
    style = data.get("style", "Professional")
    temperature = float(data.get("temperature", 0.7))
    max_tokens = int(data.get("max_tokens", 250))

    if not text:
        return jsonify({"error": "No text provided to process."}), 400

    # Build action-specific prompts
    prompts = {
        "summarize": f"Summarize the following text in a {style} style, highlighting the key points clearly:\n{text}",
        "expand":    f"Expand and elaborate on the following text in a {style} style, adding useful details:\n{text}",
        "rewrite":   f"Rewrite the following text in a {style} style, improving vocabulary and flow:\n{text}",
        "continue":  f"Continue writing the following text, matching its style ({style}) and context:\n{text}",
    }

    user_msg = prompts.get(action)
    if not user_msg:
        return jsonify({"error": "Unknown action."}), 400

    try:
        result = call_groq(SYSTEM_PROMPT, user_msg, temperature, max_tokens)
        return jsonify({"result": result})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 401
    except Exception as e:
        err = str(e)
        if "401" in err or "Unauthorized" in err:
            return jsonify({"error": "Invalid Groq API key. Please check your .env file."}), 401
        return jsonify({"error": f"API Error: {err}"}), 500


if __name__ == "__main__":
    print("\n[*] AI Text Generator server is starting...")
    print("[*] Open your browser at: http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
