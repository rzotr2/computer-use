async function setGoal() {
    const goal = document.getElementById('goal-input').value;
    if (!goal) return alert("Please enter a goal");

    const response = await fetch('/set_goal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal: goal })
    });
    const data = await response.json();
    alert("Goal set: " + data.goal);
    document.getElementById('history-list').innerHTML = '';
    refreshScreenshot();
}

async function refreshScreenshot() {
    const response = await fetch('/screenshot');
    const data = await response.json();
    if (data.image) {
        document.getElementById('screenshot').src = 'data:image/png;base64,' + data.image;
    } else {
        console.warn("Could not refresh screenshot:", data.error);
    }
}

async function takeStep(confirmed = false) {
    const btn = document.getElementById('step-btn');
    btn.disabled = true;
    btn.innerText = "Thinking...";

    try {
        const response = await fetch('/step', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ confirmed: confirmed })
        });
        const data = await response.json();

        if (data.error) {
            if (data.pending) {
                if (confirm(`Action requires confirmation: ${data.action}. Proceed?`)) {
                    takeStep(true);
                } else {
                    alert("Action cancelled.");
                }
            } else {
                alert(data.error);
            }
        } else {
            addHistoryItem(data);
            refreshScreenshot();
        }
    } catch (e) {
        console.error(e);
        alert("Error taking step");
    } finally {
        btn.disabled = false;
        btn.innerText = "Take Step";
    }
}

function addHistoryItem(item) {
    const list = document.getElementById('history-list');
    const div = document.createElement('div');
    div.className = 'history-item';
    div.innerHTML = `
        <div class="thought"><b>Thought:</b> ${item.thought}</div>
        <div class="action"><b>Action:</b> ${item.action}</div>
        <div class="result"><b>Result:</b> ${item.result}</div>
    `;
    list.prepend(div);
}

// Initial screenshot
refreshScreenshot();
