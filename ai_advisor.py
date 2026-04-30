
import os
from dotenv import load_dotenv
from typing import List, Dict
from pawpal_system import Pet

try:
    import anthropic
except ImportError:
    anthropic = None

load_dotenv()


# ----------------------------
# Prompt Builder
# ----------------------------
def build_prompt(pet: Pet) -> str:
    """Build a structured prompt from the pet's profile and task list."""
    task_lines = []
    for task in pet.get_tasks():
        task_lines.append(
            f"  - {task.title}: {task.duration_minutes} min, "
            f"{task.priority} priority, {task.time_of_day}"
        )

    tasks_text = "\n".join(task_lines) if task_lines else "  - No tasks added yet."

    return f"""You are a knowledgeable and caring pet care advisor.

A pet owner has provided the following information about their pet:

Pet Name: {pet.name}
Species: {pet.species}
Age: {pet.age} years old

Today's planned care tasks:
{tasks_text}

Please provide a short, friendly care advice summary (3-5 sentences) that:
1. Acknowledges the pet's age and species specifically
2. Comments on whether the task mix looks appropriate
3. Flags any concerns (e.g. too many high-intensity tasks, missing meals)
4. Gives one practical tip tailored to this specific pet

Keep your response concise, warm, and actionable.
Do not repeat the task list back."""


# ----------------------------
# Guardrail Validator
# ----------------------------
def validate_response(response: str) -> str:
    """Validate AI response before sending to UI.
    Returns the response if valid, or a safe fallback message."""

    fallback = (
        "[WARNING] The AI advisor is unavailable right now. "
        "Your schedule was still generated using the rule-based scheduler."
    )

    if not response or not isinstance(response, str):
        print("[GUARDRAIL] Empty or invalid response received.")
        return fallback

    if len(response.strip()) < 20:
        print("[GUARDRAIL] Response too short - likely incomplete.")
        return fallback

    if len(response.strip()) > 2000:
        print("[GUARDRAIL] Response too long - truncating.")
        return response[:2000] + "..."

    banned_phrases = ["I cannot", "I am not able", "As an AI, I"]
    for phrase in banned_phrases:
        if phrase.lower() in response.lower():
            print(f"[GUARDRAIL] Blocked phrase detected: '{phrase}'")
            return fallback

    return response.strip()


# ----------------------------
# Main Advisor Function
# ----------------------------
def get_ai_advice(pet: Pet) -> str:
    """Call the Anthropic API with the pet's profile and task list.
    Returns validated AI advice or a safe fallback message."""

    if anthropic is None:
        print("[ERROR] anthropic package is not installed.")
        return "[ERROR] AI advisor dependency missing. Install packages with: pip install -r requirements.txt"

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not found in environment.")
        return "[ERROR] API key not configured. Please add your ANTHROPIC_API_KEY to the .env file."

    try:
        client = anthropic.Anthropic(api_key=api_key)
        prompt = build_prompt(pet)

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        raw_response = message.content[0].text
        print(f"[LOG] AI response received ({len(raw_response)} chars)")
        return validate_response(raw_response)

    except anthropic.APIConnectionError:
        print("[ERROR] Could not connect to Anthropic API.")
        return "[ERROR] Connection error. Please check your internet connection."

    except anthropic.AuthenticationError:
        print("[ERROR] Invalid API key.")
        return "[ERROR] Invalid API key. Please check your .env file."

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return "[ERROR] Something went wrong with the AI advisor."


def build_chat_system_prompt(pet: Pet, schedule_summary: str) -> str:
    """Build system context for follow-up Q&A after initial advice."""

    safe_schedule_summary = schedule_summary.strip() if schedule_summary else "No schedule summary available."

    return f"""You are a knowledgeable and caring pet care advisor.

You are continuing a conversation with a pet owner.

Pet profile:
- Name: {pet.name}
- Species: {pet.species}
- Age: {pet.age} years old

Current planned schedule summary:
{safe_schedule_summary}

Instructions:
- Answer follow-up questions clearly and briefly.
- Keep advice practical, safe, and tailored to this pet.
- If a question is unrelated to pet care, gently redirect to pet-care context.
- Use a warm, supportive tone.
"""


def get_ai_chat_reply(
    pet: Pet,
    schedule_summary: str,
    chat_history: List[Dict[str, str]],
) -> str:
    """Handle follow-up chat turns after initial advice.
    chat_history must contain alternating user/assistant messages."""

    if anthropic is None:
        print("[ERROR] anthropic package is not installed.")
        return "[ERROR] AI advisor dependency missing. Install packages with: pip install -r requirements.txt"

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not found in environment.")
        return "[ERROR] API key not configured. Please add your ANTHROPIC_API_KEY to the .env file."

    # Keep recent context only to avoid unbounded prompt growth.
    recent_history = chat_history[-12:]
    formatted_messages = []
    for msg in recent_history:
        role = msg.get("role")
        content = msg.get("content", "")
        if role in ("user", "assistant") and content.strip():
            formatted_messages.append({"role": role, "content": content.strip()})

    if not formatted_messages:
        return "[ERROR] No valid chat context found."

    try:
        client = anthropic.Anthropic(api_key=api_key)
        system_prompt = build_chat_system_prompt(pet, schedule_summary)

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=system_prompt,
            messages=formatted_messages,
        )

        raw_response = message.content[0].text
        print(f"[LOG] AI chat response received ({len(raw_response)} chars)")
        return validate_response(raw_response)

    except anthropic.APIConnectionError:
        print("[ERROR] Could not connect to Anthropic API.")
        return "[ERROR] Connection error. Please check your internet connection."

    except anthropic.AuthenticationError:
        print("[ERROR] Invalid API key.")
        return "[ERROR] Invalid API key. Please check your .env file."

    except Exception as e:
        print(f"[ERROR] Unexpected error in chat reply: {e}")
        return "[ERROR] Something went wrong with the AI advisor."