import os
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from guardrails import Guard
from guardrails.hub import ToxicLanguage, DetectPII
import uuid

# Phoenix for local observability
import phoenix as px
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor

# Load environment variables
load_dotenv()

# Flask setup
app = Flask(__name__)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Launch Phoenix locally (opens web UI at http://localhost:6006)
session = px.launch_app()

# Register Phoenix tracer (sends to local Phoenix server)
tracer_provider = register(
    project_name="llm-guardrails-demo",
)

# Instrument OpenAI for automatic tracing
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

# Guardrails setup
guard = Guard().use_many(
    ToxicLanguage(threshold=0.5, validation_method="sentence", on_fail="exception"),
    DetectPII(pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD"], on_fail="fix")
)


@app.route("/ask", methods=["POST"])
def ask():
    """
    LLM API endpoint with Guardrails and Phoenix observability

    Request body:
    {
        "prompt": "Your question here",
        "user_id": "optional_user_id"
    }
    """
    data = request.json or {}
    prompt = data.get("prompt", "").strip()
    user_id = data.get("user_id", "anonymous")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    prediction_id = str(uuid.uuid4())

    response_text = ""
    guardrails_passed = True
    guardrails_actions = []
    error_message = None

    try:
        # Step 1: Validate input with Guardrails
        try:
            validated_prompt = guard.validate(prompt)
            if hasattr(validated_prompt, 'validated_output'):
                prompt = validated_prompt.validated_output
            guardrails_actions.append("Input validation passed")
        except Exception as guard_error:
            guardrails_passed = False
            guardrails_actions.append(f"Input validation failed: {str(guard_error)}")
            error_message = f"Guardrails blocked request: {str(guard_error)}"

            return jsonify({
                "error": error_message,
                "guardrails_passed": False,
                "actions": guardrails_actions,
                "prediction_id": prediction_id
            }), 400

        # Step 2: Call OpenAI API (automatically traced by Phoenix)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        response_text = completion.choices[0].message.content

        # Step 3: Validate output with Guardrails
        try:
            validated_response = guard.validate(response_text)
            if hasattr(validated_response, 'validated_output'):
                response_text = validated_response.validated_output
            guardrails_actions.append("Output validation passed")
        except Exception as guard_error:
            guardrails_passed = False
            guardrails_actions.append(f"Output validation modified response: {str(guard_error)}")
            response_text = "[Response modified by guardrails for safety]"

    except Exception as e:
        error_message = f"API Error: {str(e)}"
        response_text = "[ERROR]"
        guardrails_passed = False
        guardrails_actions.append(error_message)

    return jsonify({
        "prediction_id": prediction_id,
        "prompt": prompt,
        "response": response_text,
        "guardrails_passed": guardrails_passed,
        "guardrails_actions": guardrails_actions,
        "model": "gpt-4o-mini",
        "user_id": user_id,
        "phoenix_url": "http://localhost:6006"
    })


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "guardrails_enabled": True,
        "phoenix_observability": True,
        "phoenix_url": "http://localhost:6006",
        "project": "llm-guardrails-demo"
    })


if __name__ == "__main__":
    # Verify required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: Missing OPENAI_API_KEY in .env file")
        exit(1)

    print("=" * 70)
    print("🚀 LLM API with Guardrails & Phoenix Observability")
    print("=" * 70)
    print("\n📡 API Endpoints:")
    print("  POST /ask - Main LLM endpoint with guardrails")
    print("  GET /health - Health check")
    print("\n🔍 Phoenix Dashboard:")
    print("  http://localhost:6006")
    print("  View traces, spans, and LLM performance metrics in real-time!")
    print("\n🛡️ Guardrails Enabled:")
    print("  ✓ Toxic language detection & blocking")
    print("  ✓ PII detection & redaction")
    print("\n💡 Tip: Open http://localhost:6006 in your browser to see traces!")
    print("=" * 70)
    print("\nStarting server...\n")

    app.run(host="0.0.0.0", port=8080, debug=True)