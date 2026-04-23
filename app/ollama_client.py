import requests
import base64
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma4"

def query_ollama(prompt, image_bytes=None):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    if image_bytes:
        payload["images"] = [base64.b64encode(image_bytes).decode('utf-8')]

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"

def get_action_from_ollama(user_goal, image_bytes, action_history):
    system_prompt = """You are a PC automation assistant. You see a screenshot of a Mac OS desktop with a coordinate grid overlay.
Vertical lines are numbered 0-10 (X axis). Horizontal lines are labeled A-K (Y axis).
Your goal is: {user_goal}
Action History: {action_history}

Analyze the screenshot and decide the next single action to move towards the goal.
Available actions:
- MOVE_TO(X, Y): Move mouse to grid intersection or relative position (e.g., 5, B).
- CLICK(): Click left mouse button.
- DOUBLE_CLICK(): Double click left mouse button.
- TYPE("text"): Type the specified text.
- PRESS("key"): Press a specific key (e.g., "enter", "command", "space").
- RUN_COMMAND("command"): Run a terminal command.
- DONE: If the goal is reached.

Provide your response in JSON format with two fields:
1. "thought": Your reasoning for this action.
2. "action": The action string (e.g., 'MOVE_TO(5, B)').

Example:
{{"thought": "I need to open the browser, which is located at bottom dock.", "action": "MOVE_TO(5, K)"}}
"""
    prompt = system_prompt.format(user_goal=user_goal, action_history=action_history)
    return query_ollama(prompt, image_bytes)
