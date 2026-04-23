import pyautogui
import subprocess
import re
import json

# Safety settings
pyautogui.PAUSE = 1.0
pyautogui.FAILSAFE = True

def parse_coordinate(coord_str, max_val, grid_size=100):
    """
    Parses a coordinate from the grid system (0-100).
    Maps it to pixel coordinates.
    """
    try:
        val = float(coord_str)
    except ValueError:
        return 0

    # Map to pixels
    pixel_coord = (val / grid_size) * max_val
    return int(pixel_coord)

def execute_action(action_str):
    """
    Parses and executes an action string.
    """
    width, height = pyautogui.size()

    # MOVE_TO(X, Y)
    move_match = re.match(r"MOVE_TO\(([^,]+),\s*([^)]+)\)", action_str)
    if move_match:
        x_raw = move_match.group(1)
        y_raw = move_match.group(2)
        x = parse_coordinate(x_raw, width)
        y = parse_coordinate(y_raw, height)
        pyautogui.moveTo(x, y)
        return f"Moved to ({x}, {y})"

    # CLICK()
    if action_str == "CLICK()":
        pyautogui.click()
        return "Clicked"

    # DOUBLE_CLICK()
    if action_str == "DOUBLE_CLICK()":
        pyautogui.doubleClick()
        return "Double clicked"

    # TYPE("text")
    type_match = re.match(r'TYPE\("(.+)"\)', action_str)
    if type_match:
        text = type_match.group(1)
        pyautogui.write(text)
        return f"Typed: {text}"

    # PRESS("key") or PRESS("key1+key2")
    press_match = re.match(r'PRESS\("(.+)"\)', action_str)
    if press_match:
        keys_str = press_match.group(1)
        if "+" in keys_str:
            keys = [k.strip() for k in keys_str.split("+")]
            pyautogui.hotkey(*keys)
            return f"Hotkey pressed: {' + '.join(keys)}"
        else:
            pyautogui.press(keys_str)
            return f"Pressed: {keys_str}"

    # RUN_COMMAND("command")
    cmd_match = re.match(r'RUN_COMMAND\("(.+)"\)', action_str)
    if cmd_match:
        cmd = cmd_match.group(1)
        # For safety, you might want to prompt the user here in a real scenario
        # But as per requirements, we implement it.
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return f"Executed command: {cmd}\nOutput: {result.stdout[:100]}"

    if action_str == "DONE":
        return "GOAL REACHED"

    return f"Unknown action: {action_str}"

def process_ollama_response(response_text):
    try:
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            return data
        else:
            return {"thought": "Could not parse JSON from Ollama", "action": "NONE"}
    except Exception as e:
        return {"thought": f"Error parsing response: {str(e)}", "action": "NONE"}
