import os
from typing import List, Dict, Any

from flask import Flask, jsonify, render_template, request
from openai import OpenAI, OpenAIError


app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("The OPENAI_API_KEY environment variable must be set.")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "You are a helpful and friendly AI assistant having a conversation with the user. "
    "Keep your replies concise, clear, and engaging."
)


def build_messages(history: List[Dict[str, str]], user_message: str) -> List[Dict[str, Any]]:
    messages: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": [{"type": "text", "text": SYSTEM_PROMPT}],
        }
    ]

    for message in history:
        role = message.get("role")
        content = message.get("content", "")
        if role not in {"user", "assistant"} or not content:
            continue
        messages.append(
            {
                "role": role,
                "content": [{"type": "text", "text": content}],
            }
        )

    messages.append(
        {
            "role": "user",
            "content": [{"type": "text", "text": user_message}],
        }
    )
    return messages


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat() -> Any:
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not user_message:
        return jsonify({"error": "Message is required."}), 400

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            messages=build_messages(history, user_message),
        )
        reply = response.output_text
    except OpenAIError as exc:
        return (
            jsonify({"error": "Failed to contact OpenAI API.", "details": str(exc)}),
            500,
        )

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
