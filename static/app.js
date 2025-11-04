const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

const history = [];

function appendMessage(role, content) {
  const message = document.createElement("div");
  message.classList.add("message", role);
  message.innerText = content;
  chatLog.appendChild(message);
  chatLog.scrollTop = chatLog.scrollHeight;
}

async function sendMessage(event) {
  event.preventDefault();
  const message = userInput.value.trim();
  if (!message) {
    return;
  }

  appendMessage("user", message);
  history.push({ role: "user", content: message });
  userInput.value = "";
  userInput.disabled = true;
  sendButton.disabled = true;

  appendMessage("assistant", "Thinking…");
  const typingIndicator = chatLog.lastElementChild;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: "Unknown error." }));
      throw new Error(error.error || "Failed to send message.");
    }

    const data = await response.json();
    typingIndicator.remove();
    appendMessage("assistant", data.reply);
    history.push({ role: "assistant", content: data.reply });
  } catch (error) {
    typingIndicator.remove();
    appendMessage("assistant", `Error: ${error.message}`);
  } finally {
    userInput.disabled = false;
    sendButton.disabled = false;
    userInput.focus();
  }
}

chatForm.addEventListener("submit", sendMessage);
userInput.focus();
