import os
from dotenv import load_dotenv
from openai import OpenAI
from guardrails import Guard
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

# Define a structured response model
class MsgOutput(BaseModel):
    message: str

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Apply Guardrails schema
guard = Guard.for_pydantic(
    output_class=MsgOutput,
    description="The model must return JSON: { message: string }"
)

prompt = "Say hello in a structured JSON format with a 'message' field."

# Call OpenAI Chat API
raw = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],  # type: ignore
    response_format={"type": "json_object"}  # type: ignore
)

# Get the response content
output_text = raw.choices[0].message.content

# Validate output
validated = guard.validate(output_text)

print("\nRAW OUTPUT:")
print(output_text)

print("\nVALIDATED OUTPUT:")
print(validated.validated_output)
