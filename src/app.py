import os
from flask import Flask, request, jsonify
from openai import OpenAI
from openai.types import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam

# Optional: Guardrails
try:
    from guardrails import Guard
    GUARDRAILS_AVAILABLE = True
except ImportError:
    GUARDRAILS_AVAILABLE = False

# Flask setup
app = Flask(__name__)

# OpenAI client (v1)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Guardrails setup
if GUARDRAILS_AVAILABLE:
    guard = Guard().use("safety")  # minimal safety guard

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json or {}
    prompt = data.get("prompt", "Hello").strip()[:2000]

    # Prepare typed messages
    messages = [ChatCompletionUserMessageParam(content=prompt)]

    response_text = ""
    try:
        if GUARDRAILS_AVAILABLE:
            # Wrap the call with Guardrails
            result = guard(
                client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=200
                )
            )
            # Guard result may be dict or str
            if isinstance(result, dict):
                response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                response_text = str(result)
        else:
            # Direct OpenAI call
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=200
            )
            response_text = res.choices[0].message.content

    except Exception as e:
        response_text = f"[ERROR] {str(e)}"

    return jsonify({"prompt": prompt, "response": response_text})


if __name__ == "__main__":
    # Run Flask server on port 8080
    app.run(port=8080, debug=True)
