import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from the .env file
load_dotenv()

# Model and system prompts as specified in requirements
MODEL_NAME = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = "You are a professional AI writing assistant that generates clear, meaningful, and grammatically correct text."

def get_groq_client():
    """
    Initializes and returns the Groq API client.
    Raises a ValueError if the GROQ_API_KEY is not set or contains the default placeholder.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key.strip() == "your_groq_api_key_here":
        raise ValueError(
            "Groq API Key is missing or not configured. "
            "Please set your GROQ_API_KEY in the '.env' file or your system environment variables."
        )
    return Groq(api_key=api_key)

def call_groq_api(system_msg: str, user_msg: str, temperature: float, max_tokens: int) -> str:
    """
    Core function to communicate with the Groq API.
    Handles authentication, connection errors, and other API exceptions gracefully.
    """
    try:
        # Get configured client
        client = get_groq_client()
        
        # Request completion
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
        
    except ValueError as ve:
        # Catch local configuration errors
        return f"Configuration Error: {str(ve)}"
        
    except Exception as e:
        # Catch external API/Network errors
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            return "Authentication Error: The provided Groq API key is invalid. Please check your credentials."
        elif "Connection" in error_msg or "connect" in error_msg.lower():
            return "Connection Error: Failed to connect to Groq API. Please check your internet connection."
        else:
            return f"API Error: {error_msg}"

def generate_text(prompt: str, style: str, temperature: float, max_tokens: int) -> str:
    """
    Validates inputs and triggers standard text generation with the system prompt and style guidelines.
    """
    if not prompt or not prompt.strip():
        return "Validation Error: Prompt cannot be empty. Please enter some text."
        
    # Style combination user prompt
    user_prompt = f"Generate a {style} response for the following request:\n{prompt.strip()}"
    
    return call_groq_api(SYSTEM_PROMPT, user_prompt, temperature, max_tokens)

def process_modification(action_type: str, prompt: str, current_output: str, style: str, temperature: float, max_tokens: int) -> str:
    """
    Processes text modification options (Summarize, Expand, Rewrite, Continue Writing).
    It prioritizes prompt text, but if empty, processes existing output text.
    """
    # Decide which text to process: prompt is prioritized; if empty, use current_output.
    text_to_process = prompt.strip() if prompt else ""
    if not text_to_process:
        text_to_process = current_output.strip() if current_output else ""
        
    if not text_to_process:
        return "Validation Error: No text found. Please write something in the Prompt or generate text first."
        
    # Map actions to system prompt or modified user prompts
    if action_type == "summarize":
        user_prompt = f"Summarize the following text in a {style} style, highlighting the key points clearly and concisely:\n{text_to_process}"
    elif action_type == "expand":
        user_prompt = f"Expand and elaborate on the following text in a {style} style, adding details and context while keeping the core message:\n{text_to_process}"
    elif action_type == "rewrite":
        user_prompt = f"Rewrite the following text in a {style} style, improving vocabulary, sentence structure, and overall flow:\n{text_to_process}"
    elif action_type == "continue":
        user_prompt = f"Continue writing the following text, matching its style ({style}) and context seamlessly, adding logical progression:\n{text_to_process}"
    else:
        return "Validation Error: Unknown action requested."
        
    return call_groq_api(SYSTEM_PROMPT, user_prompt, temperature, max_tokens)
