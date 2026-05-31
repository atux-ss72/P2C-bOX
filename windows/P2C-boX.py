import asyncio
import subprocess
import re
import threading
import tkinter as tk

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

clients = []
usernames = {}

# ===================== 🌐 FULL UI ===================== #
html = """
<!DOCTYPE html>
<html>
<head>
<title>P2C Chat</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
body {
    margin: 0;
    font-family: Arial;
    background: linear-gradient(to bottom, #071a2f, #000);
    color: white;
    display: flex;
    flex-direction: column;
    height: 100vh;
}

h1 {
    color: #4da3ff;
    margin: 10px 0;
    font-size: 28px;
    text-align: center;
}

#users {
    position: fixed;
    right: 10px;
    top: 10px;
    background: rgba(0,0,0,0.6);
    padding: 10px;
    font-size: 12px;
}

#chat-box {
    flex: 1;
    overflow-y: auto;
    padding: 10px;
    background: rgba(0,0,0,0.5);
}

.message {
    margin: 5px 0;
}

#input-area {
    display: flex;
    padding: 8px;
    background: #000;
}

#message {
    flex: 1;
    padding: 12px;
    border: none;
    background: #111;
    color: white;
    outline: none;
}

#send-btn {
    margin-left: 5px;
    padding: 12px;
    background: #2ecc71;
    border: none;
    color: white;
}

/* Modal */
#modal {
    position: fixed;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.85);
    display: flex;
    justify-content: center;
    align-items: center;
}

#modal-box {
    background: #071a2f;
    padding: 20px;
    border-radius: 10px;
    width: 80%;
    max-width: 300px;
}

#modal input {
    width: 100%;
    padding: 10px;
    border: 2px solid #4da3ff;
    background: transparent;
    color: white;
}

#modal button {
    padding: 10px;
    background: #4da3ff;
    border: none;
    color: white;
    width: 100%;
}

/* 📱 Mobile */
@media (max-width: 600px) {
    #users {
        position: static;
        width: 100%;
        text-align: center;
        background: #111;
    }
}
</style>
</head>

<body>

<h1>P2C</h1>

<div id="modal">
    <div id="modal-box">
        <h3>Enter Username</h3>
        <input id="modal-username" placeholder="Username..." />
        <br><br>
        <button onclick="setUsername()">Start</button>
    </div>
</div>

<div id="users">
<b>Users</b>
<div id="user-list"></div>
</div>

<div id="chat-box"></div>

<div id="input-area">
    <input id="message" placeholder="Type a message..." />
    <button id="send-btn">➤</button>
</div>

<script>
let username = localStorage.getItem("username") || "";
let ws;
let isConnected = false;

const modal = document.getElementById("modal");
const modalInput = document.getElementById("modal-username");
const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("message");
const sendBtn = document.getElementById("send-btn");

function connectWS() {
    ws = new WebSocket(
        (location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/ws"
    );

    ws.onopen = () => {
        isConnected = true;
        console.log("Connected");

        if (username) {
            ws.send(JSON.stringify({type:"join", user:username}));
        }
    };

    ws.onmessage = (event) => {
        let data = JSON.parse(event.data);

        if (data.type === "message") {
            let div = document.createElement("div");
            div.className = "message";
            div.textContent = data.user + ": " + data.text;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        if (data.type === "users") {
            let list = document.getElementById("user-list");
            list.innerHTML = "";
            data.users.forEach(u => {
                let d = document.createElement("div");
                d.textContent = u;
                list.appendChild(d);
            });
        }
    };

    ws.onclose = () => {
        isConnected = false;
        setTimeout(connectWS, 2000);
    };
}

connectWS();

if (!username) {
    modal.style.display = "flex";
} else {
    modal.style.display = "none";
}

function setUsername() {
    let name = modalInput.value.trim();
    if (!name) return;

    username = name;
    localStorage.setItem("username", username);
    modal.style.display = "none";

    if (isConnected) {
        ws.send(JSON.stringify({type:"join", user:username}));
    }
}

function sendMessage() {
    let msg = messageInput.value.trim();
    if (!msg || !username || !isConnected) return;

    ws.send(JSON.stringify({type:"message", text:msg}));
    messageInput.value = "";
}

sendBtn.onclick = sendMessage;

messageInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

messageInput.addEventListener("focus", () => {
    setTimeout(() => window.scrollTo(0, document.body.scrollHeight), 300);
});

modalInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") setUsername();
});
</script>

</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

# ===================== 💬 WebSocket ===================== #
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)

    try:
        while True:
            data = await ws.receive_json()

            if data["type"] == "join":
                usernames[ws] = data["user"]
                await broadcast_users()

            elif data["type"] == "message":
                await broadcast_message(usernames.get(ws, "Anon"), data["text"])

    except WebSocketDisconnect:
        clients.remove(ws)
        usernames.pop(ws, None)
        await broadcast_users()

async def broadcast_message(user, text):
    for c in clients:
        await c.send_json({"type": "message", "user": user, "text": text})

async def broadcast_users():
    user_list = list(usernames.values())
    for c in clients:
        await c.send_json({"type": "users", "users": user_list})

# ===================== 🌍 POPUP ===================== #
def show_popup(link):
    root = tk.Tk()
    root.title("Chat Link")
    root.geometry("420x150")

    tk.Label(root, text="Share this link:").pack(pady=10)

    entry = tk.Entry(root, width=50)
    entry.insert(0, link)
    entry.pack()

    def copy():
        root.clipboard_clear()
        root.clipboard_append(link)

    tk.Button(root, text="Copy", command=copy).pack(pady=10)

    root.mainloop()

# ===================== 🚇 CLOUDFLARE ===================== #
def start_tunnel():
    process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://localhost:8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in process.stdout:
        match = re.search(r"https://.*trycloudflare.com", line)
        if match:
            link = match.group(0)
            print("PUBLIC LINK:", link)
            threading.Thread(target=show_popup, args=(link,), daemon=True).start()
            break

# ===================== 🚀 MAIN ===================== #
def run_all():
    threading.Thread(target=start_tunnel, daemon=True).start()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=None,
        access_log=False
    )

if __name__ == "__main__":
    run_all()