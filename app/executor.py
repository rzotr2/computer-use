import pyautogui
import subprocess
import re
import json

# Safety settings
pyautogui.PAUSE = 1.0
pyautogui.FAILSAFE = True

import mss

def get_scaling_factor():
    """
    Returns the scaling factor between physical pixels and logical points.
    Retina displays often have a scaling factor of 2.0.
    """
    logical_width, logical_height = pyautogui.size()
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        physical_width = monitor["width"]
        physical_height = monitor["height"]

    scale_x = physical_width / logical_width
    scale_y = physical_height / logical_height
    return scale_x, scale_y

def parse_coordinate(coord_str, logical_max, grid_size=100):
    """
    Parses a coordinate from the grid system (0-100).
    Maps it to LOGICAL pixel coordinates (which pyautogui uses).
    Note: The screenshot is in PHYSICAL pixels.
    """
    try:
        val = float(coord_str)
    except ValueError:
        return 0

    # Map to logical points
    # (val / grid_size) gives the fraction of the PHYSICAL screen.
    # We need to map this to the same fraction of the LOGICAL screen.
    logical_coord = (val / grid_size) * logical_max
    return int(logical_coord)

def execute_action(action_str):
    """
    Parses and executes an action string.
    """
    logical_width, logical_height = pyautogui.size()
    scale_x, scale_y = get_scaling_factor()
    print(f"DEBUG: Logical size: {logical_width}x{logical_height}, Scaling: {scale_x}x{scale_y}")

    # MOVE_TO(X, Y)
    move_match = re.match(r"MOVE_TO\(([^,]+),\s*([^)]+)\)", action_str)
    if move_match:
        x_raw = move_match.group(1)
        y_raw = move_match.group(2)
        x = parse_coordinate(x_raw, logical_width)
        y = parse_coordinate(y_raw, logical_height)
        pyautogui.moveTo(x, y)
        return f"Moved to logical coords ({x}, {y})"

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
