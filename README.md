# PC Controller Agent

A local macOS automation tool that uses the **Ollama gemma4** vision model to understand your screen and execute actions based on your natural language goals.

## Features

- **Multimodal Understanding**: Uses gemma4 to analyze screenshots with a coordinate grid overlay.
- **Full Control**: Can move the mouse, click, type, and execute terminal commands.
- **Safety Confirmation**: Sensitive actions (like terminal commands) require user approval in the Web UI.
- **100% Local**: No data leaves your machine. Everything runs on your local Ollama instance.

## Prerequisites

1.  **macOS**: This app is designed to run on macOS.
2.  **Ollama**: Install Ollama from [ollama.com](https://ollama.com).
3.  **Gemma 4**: Pull the model:
    ```bash
    ollama pull gemma4
    ```
4.  **Python 3.9+**: Ensure you have Python installed.

## Installation

1.  Clone this repository or download the source code.
2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Running the App

1.  Start the FastAPI server:
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```
2.  Open your browser and navigate to:
    ```
    http://localhost:8000
    ```

## Usage

1.  **Set a Goal**: Enter what you want the agent to do in the input box (e.g., "Find a picture of a cat on my desktop and move it to the trash" or "Open Notes and write a reminder").
2.  **Take Step**: Click the "Take Step" button. The agent will capture the screen, think about the next move, and show its reasoning.
3.  **Confirm Actions**: If the agent decides to run a terminal command, a confirmation dialog will appear in the browser.
4.  **Action History**: You can see a list of executed actions and the agent's "thoughts" on the right side of the screen.

## Note on Permissions

Because this app controls your mouse and keyboard, macOS will ask for **Accessibility** and **Screen Recording** permissions when you first run it. Please grant these in **System Settings > Privacy & Security**.

## Disclaimer

This is a powerful tool that can execute commands on your machine. Always review the agent's proposed actions, especially when it requests to run terminal commands.
