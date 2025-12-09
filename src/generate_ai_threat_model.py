import os
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from guardrails import Guard
from guardrails.hub import ToxicLanguage, DetectPII
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

# Flask setup
app = Flask(__name__)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Guardrails Setup
guard = Guard()
guard.add(ToxicLanguage(threshold=0.5))
guard.add(DetectPII())

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()

        prompt = data.get("prompt", "")
        user_id = data.get("user_id", "anonymous")

        if not prompt:
            return jsonify({"error": "Missing 'prompt'"}), 400

        # Apply Guardrails validation on the input
        guard.validate(prompt)

        # Call OpenAI (Correct Endpoint)
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            metadata={
                "user_id": user_id,
                "request_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        ai_text = response.output_text

        return jsonify({
            "user_id": user_id,
            "response": ai_text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)



