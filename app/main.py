import sys
import os
from unittest.mock import MagicMock

# Set DISPLAY to avoid pyautogui errors in headless environments
if 'DISPLAY' not in os.environ:
    os.environ['DISPLAY'] = ':0'

# Mock OS-dependent libraries for testing environments
try:
    import pyautogui
except Exception:
    mock_pyautogui = MagicMock()
    sys.modules["pyautogui"] = mock_pyautogui

try:
    import mss
except Exception:
    mock_mss = MagicMock()
    sys.modules["mss"] = mock_mss

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import base64

from .screenshot import capture_screen_with_grid, get_screenshot_bytes
from .ollama_client import get_action_from_ollama
from .executor import process_ollama_response, execute_action

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class GoalRequest(BaseModel):
    goal: str

class StepRequest(BaseModel):
    confirmed: bool = False

# Global state to keep track of history
action_history = []
current_goal = ""
pending_action = None

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html") as f:
        return f.read()

@app.post("/set_goal")
async def set_goal(request: GoalRequest):
    global current_goal, action_history, pending_action
    current_goal = request.goal
    action_history = []
    pending_action = None
    return {"status": "Goal set", "goal": current_goal}

@app.get("/screenshot")
async def get_screenshot():
    try:
        img = capture_screen_with_grid()
        img_bytes = get_screenshot_bytes(img)
        return JSONResponse(content={
            "image": base64.b64encode(img_bytes).decode('utf-8')
        })
    except Exception as e:
        return JSONResponse(content={
            "image": "",
            "error": str(e)
        })

@app.post("/step")
async def execute_step(request: StepRequest):
    global current_goal, action_history, pending_action

    if not current_goal:
        return {"error": "No goal set"}

    # If we had a pending sensitive action and it's now confirmed
    if pending_action and request.confirmed:
        action = pending_action["action"]
        result = execute_action(action)
        history_entry = {
            "thought": f"Confirmed: {pending_action['thought']}",
            "action": action,
            "result": result
        }
        action_history.append(history_entry)
        pending_action = None
        return history_entry
    elif pending_action:
        return {"error": "Action requires confirmation", "pending": True, "action": pending_action["action"]}

    # 1. Capture screen
    try:
        img = capture_screen_with_grid()
        img_bytes = get_screenshot_bytes(img)
    except Exception as e:
        return {"error": f"Failed to capture screen: {str(e)}"}

    # 2. Query Ollama
    response_text = get_action_from_ollama(current_goal, img_bytes, action_history)

    # 3. Process response
    action_data = process_ollama_response(response_text)
    thought = action_data.get("thought", "No thought provided")
    action = action_data.get("action", "NONE")

    # 4. Handle sensitive actions
    if "RUN_COMMAND" in action:
        pending_action = {"thought": thought, "action": action}
        return {"thought": thought, "action": action, "result": "WAITING FOR CONFIRMATION", "pending": True}

    # 5. Execute normal action
    result = "No action taken"
    if action and action != "NONE":
        try:
            result = execute_action(action)
        except Exception as e:
            result = f"Error executing action: {str(e)}"

    # 6. Update history
    history_entry = {
        "thought": thought,
        "action": action,
        "result": result
    }
    action_history.append(history_entry)

    return history_entry

@app.get("/history")
async def get_history():
    return {"history": action_history}
