import json
import time
import os
import re
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

from dotenv import load_dotenv

# Automatically load environment variables from .env file
load_dotenv()

# Load credentials from environment variables for security
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8740152123:AAH7z32zQpmeNR3rVpZjeCEqo0ZXDMaHmG8")
AIPIPE_TOKEN = os.environ.get(
    "AIPIPE_TOKEN",
    "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjIwMDYxNjdAZHMuc3R1ZHkuaWl0bS5hYy5pbiIsImlhdCI6MTc4NDg5NzY1NiwiaXNzIjoiaHR0cHM6Ly9haXBpcGUub3JnIiwiYXVkIjoiYWlwaXBlLWFwaSIsImV4cCI6MTc4NTUwMjQ1Nn0.KGOXZn0DjQRuXqXmp6LWiuxYNmorw-DWV6ebv1YR1gs"
)
LOG_URL = os.environ.get("LOG_URL", "https://raw.githubusercontent.com/shitanshuchaurasiya/TDS_ga5/main/run.jsonl")

# Initialize OpenAI client with AIPipe endpoint
client = OpenAI(base_url="https://aipipe.org/openai/v1", api_key=AIPIPE_TOKEN)
LOG_FILE = "run.jsonl"

# Per-chat conversation history tracking for multi-turn questions
conversation_history = {}

def log_event(event: dict):
    """Write an event log line to run.jsonl with a timestamp."""
    event["timestamp"] = time.time()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

def clean_and_parse_json(text: str) -> dict:
    """Extract and parse valid JSON from LLM response text."""
    text = text.strip()
    
    # Attempt direct JSON parsing first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Extract content inside ```json ... ``` or ``` ... ```
    code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1))
        except json.JSONDecodeError:
            pass

    # Extract content between outermost { and }
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Failed to parse valid JSON object from response: {text}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user_text = update.message.text
    
    # Log incoming message
    log_event({"type": "incoming", "chat_id": chat_id, "text": user_text})

    # Track conversation history (keep last 6 turns)
    history = conversation_history.setdefault(chat_id, [])
    history.append({"role": "user", "content": user_text})

    # System prompt enforcing strict JSON shape
    system_prompt = (
        "You are an expert data analyst. The user's LAST message contains a data-analysis question "
        "and specifies the exact JSON object structure required in the reply.\n"
        "1. Compute or look up the accurate answer to the user's question.\n"
        "2. Match the requested JSON shape EXACTLY. Do not add extra keys or omit requested keys.\n"
        "3. Output ONLY the raw valid JSON object. Do not include markdown formatting, code blocks (no ```json), "
        "explanations, or extra conversational text."
    )

    messages = [{"role": "system", "content": system_prompt}] + history[-6:]

    try:
        try:
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=messages,
                temperature=0.1
            )
        except Exception as api_err:
            print(f"Primary model error: {api_err}. Falling back to gpt-4o-mini...")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.1
            )

        reply_text = response.choices[0].message.content.strip()
        parsed_json = clean_and_parse_json(reply_text)
    except Exception as err:
        print(f"Error generating/parsing response: {err}")
        # Fallback JSON structure matching common format
        parsed_json = {"answer": f"Error: {str(err)}"}

    # Ensure log_url key is included in response
    parsed_json["log_url"] = LOG_URL
    final_reply = json.dumps(parsed_json, ensure_ascii=False)

    # Save bot response to conversation history & log event
    history.append({"role": "assistant", "content": final_reply})
    log_event({"type": "outgoing", "chat_id": chat_id, "text": final_reply})

    await update.message.reply_text(final_reply)

def main():
    if TELEGRAM_BOT_TOKEN in ("YOUR_BOTFATHER_TOKEN_HERE", ""):
        print("WARNING: TELEGRAM_BOT_TOKEN environment variable is not set!")
        print("Please set TELEGRAM_BOT_TOKEN before running the bot.")

    print("Initializing Data Analyst Telegram Bot...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running... (Press Ctrl+C to stop)")
    app.run_polling()

if __name__ == "__main__":
    main()
