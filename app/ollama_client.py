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
    system_prompt = """You are a PC automation assistant. You see a screenshot of a Mac OS desktop with a high-precision coordinate grid overlay.
The grid is 100x100.
X-axis (vertical lines) ranges from 0 to 100 (left to right).
Y-axis (horizontal lines) ranges from 0 to 100 (top to bottom).
Major lines and labels are drawn every 10 units with white backgrounds for readability. Minor lines are drawn every 1 unit.

To be precise:
1. Identify the target UI element.
2. Look at the nearest major grid labels (the numbers in white boxes).
3. Use the minor lines to find the exact coordinate.
4. The center of the screen is (50, 50). The top-left is (0, 0).

Your goal is: {user_goal}
Action History: {action_history}

Analyze the screenshot, identify UI elements, and decide the next single action.
Available actions:
- MOVE_TO(X, Y): Move mouse to specific coordinates (e.g., 55.5, 20). Use floats for sub-grid precision if needed.
- CLICK(): Click left mouse button.
- DOUBLE_CLICK(): Double click left mouse button.
- TYPE("text"): Type the specified text.
- PRESS("key"): Press a specific key (e.g., "enter", "command", "space"). You can use combinations like "command+t" or "shift+enter".
- RUN_COMMAND("command"): Run a terminal command.
- DONE: ONLY if the goal is reached and YOU HAVE VERIFIED it on the current screenshot.

DO NOT assume success. Always verify the state of the UI in the current screenshot before declaring the task finished.
If the previous action didn't work as expected, try a different approach.

Provide your response in JSON format with two fields:
1. "thought": Your reasoning for this action, specifically describing what UI element you are targeting and its approximate coordinates.
2. "action": The action string (e.g., 'MOVE_TO(42, 88)').

Example:
{{"thought": "I need to click the Apple icon at the top left, which is around (2, 2).", "action": "MOVE_TO(2, 2)"}}
"""
    prompt = system_prompt.format(user_goal=user_goal, action_history=action_history)
    return query_ollama(prompt, image_bytes)
