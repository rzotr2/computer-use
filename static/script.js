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

let isAuto = false;

async function takeStep(confirmed = false) {
    const btn = document.getElementById('step-btn');
    if (!isAuto) {
        btn.disabled = true;
        btn.innerText = "Thinking...";
    }

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
                    return await takeStep(true);
                } else {
                    alert("Action cancelled.");
                    stopAuto();
                }
            } else {
                alert(data.error);
                stopAuto();
            }
        } else {
            addHistoryItem(data);
            refreshScreenshot();

            if (isAuto && data.action !== "DONE") {
                // Wait 1 second before next step in auto mode
                setTimeout(takeStep, 1000);
            } else if (data.action === "DONE") {
                stopAuto();
            }
        }
    } catch (e) {
        console.error(e);
        alert("Error taking step");
        stopAuto();
    } finally {
        if (!isAuto) {
            btn.disabled = false;
            btn.innerText = "Take Step";
        }
    }
}

function toggleAuto() {
    if (isAuto) {
        stopAuto();
    } else {
        startAuto();
    }
}

function startAuto() {
    isAuto = true;
    const btn = document.getElementById('auto-btn');
    btn.innerText = "Stop Autonomous";
    btn.style.backgroundColor = "#dc3545";
    btn.style.color = "white";
    takeStep();
}

function stopAuto() {
    isAuto = false;
    const btn = document.getElementById('auto-btn');
    btn.innerText = "Start Autonomous";
    btn.style.backgroundColor = "";
    btn.style.color = "";

    const stepBtn = document.getElementById('step-btn');
    stepBtn.disabled = false;
    stepBtn.innerText = "Take Step";
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
