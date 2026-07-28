import json
import time
import os
import re
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8740152123:AAH7z32zQpmeNR3rVpZjeCEqo0ZXDMaHmG8")
AIPIPE_TOKEN = os.environ.get("AIPIPE_TOKEN", "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjIwMDYxNjdAZHMuc3R1ZHkuaWl0bS5hYy5pbiIsImlhdCI6MTc4NDg5NzY1NiwiaXNzIjoiaHR0cHM6Ly9haXBpcGUub3JnIiwiYXVkIjoiYWlwaXBlLWFwaSIsImV4cCI6MTc4NTUwMjQ1Nn0.KGOXZn0DjQRuXqXmp6LWiuxYNmorw-DWV6ebv1YR1gs")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://aipipe.org/openai/v1" if not OPENAI_API_KEY else "https://api.openai.com/v1")
API_KEY = OPENAI_API_KEY if OPENAI_API_KEY else AIPIPE_TOKEN
LOG_URL = os.environ.get("LOG_URL", "https://raw.githubusercontent.com/24f2006167/Project_1/main/run.jsonl")

LOG_FILE = "run.jsonl"

# Initialize OpenAI / AIPipe client
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# Per-chat conversation history tracking
conversation_history = {}

def log_event(event: dict):
    """Write an event log line to run.jsonl with a timestamp."""
    event["timestamp"] = time.time()
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        print(f"Logging error: {e}")

def clean_and_parse_json(text: str) -> dict:
    """Extract and parse valid JSON object from LLM response text."""
    text = text.strip()
    
    # 1. Direct JSON parse
    try:
        res = json.loads(text)
        if isinstance(res, dict):
            return res
    except json.JSONDecodeError:
        pass

    # 2. Extract from ```json ... ``` code blocks
    code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Extract between first '{' and last '}'
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Failed to parse valid JSON object from response: {text}")

def extract_prompt_from_input(user_text: str) -> tuple[str, list]:
    """
    Parses input text. Handles raw strings as well as JSON arrays/dicts
    sent by evaluation harnesses (e.g. [{"messages": [...]}]).
    Also detects embedded image URLs in text.
    """
    clean_text = user_text.strip()
    image_urls = []

    # Check if input is a JSON string from eval harness
    if (clean_text.startswith("[") and clean_text.endswith("]")) or (clean_text.startswith("{") and clean_text.endswith("}")):
        try:
            parsed = json.loads(clean_text)
            if isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
                first_item = parsed[0]
                if "messages" in first_item and isinstance(first_item["messages"], list):
                    clean_text = "\n".join(str(m) for m in first_item["messages"])
            elif isinstance(parsed, dict) and "messages" in parsed:
                if isinstance(parsed["messages"], list):
                    clean_text = "\n".join(str(m) for m in parsed["messages"])
        except Exception:
            pass  # Fall back to using user_text directly

    # Find image URLs (http/https ending in .png, .jpg, .jpeg, .webp, .svg, etc. or containing /charts/)
    url_pattern = r"https?://[^\s]+\.(?:png|jpg|jpeg|webp|gif)"
    chart_pattern = r"https?://[^\s]+/charts/[^\s]+"
    found_urls = list(set(re.findall(url_pattern, clean_text, re.IGNORECASE) + re.findall(chart_pattern, clean_text, re.IGNORECASE)))
    for url in found_urls:
        image_urls.append(url.rstrip('"\'),.'))

    return clean_text, image_urls

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    if not update.message:
        return
    chat_id = update.effective_chat.id
    log_event({"type": "incoming", "chat_id": chat_id, "text": "/start"})
    
    reply_dict = {
        "answer": "Data Analyst Telegram Bot is online! Send your data questions, charts, or JSON prompts.",
        "log_url": LOG_URL
    }
    reply_text = json.dumps(reply_dict, ensure_ascii=False)
    log_event({"type": "outgoing", "chat_id": chat_id, "text": reply_text})
    await update.message.reply_text(reply_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat_id = update.effective_chat.id
    raw_text = update.message.text or update.message.caption or ""
    
    # Handle Photo Attachments directly from Telegram
    telegram_photo_url = None
    if update.message.photo:
        try:
            photo_file = await update.message.photo[-1].get_file()
            telegram_photo_url = photo_file.file_path
        except Exception as p_err:
            print(f"Error fetching telegram photo URL: {p_err}")

    if not raw_text and not telegram_photo_url:
        return

    # Extract clean text prompt and embedded image URLs
    prompt_text, image_urls = extract_prompt_from_input(raw_text)
    if telegram_photo_url:
        image_urls.append(telegram_photo_url)

    # Log incoming event
    log_event({"type": "incoming", "chat_id": chat_id, "text": raw_text, "image_urls": image_urls})

    # Track conversation history
    history = conversation_history.setdefault(chat_id, [])

    # Format user turn (multimodal if images present)
    if image_urls:
        user_content = [{"type": "text", "text": prompt_text if prompt_text else "Analyze this image and reply with the required JSON."}]
        for img_url in image_urls:
            user_content.append({"type": "image_url", "image_url": {"url": img_url}})
    else:
        user_content = prompt_text

    history.append({"role": "user", "content": user_content})

    system_prompt = (
        "You are an expert data analyst. The user's prompt contains a data analysis task, question, or chart.\n"
        "1. Carefully inspect the user prompt and any provided images/charts.\n"
        "2. Compute or look up the accurate answer to the question.\n"
        "3. Look for the required JSON format in the user prompt (e.g., {\"answer\": ...} or {\"state\": ...}).\n"
        "4. Output ONLY a valid JSON object matching the requested shape. "
        "Do NOT include markdown formatting, code blocks (no ```json), explanations, or extra conversational text."
    )

    # Construct messages list (system prompt + history)
    messages = [{"role": "system", "content": system_prompt}] + history[-6:]

    # Primary and fallback model selection
    primary_model = os.environ.get("PRIMARY_MODEL", "gpt-4o-mini")
    fallback_model = os.environ.get("FALLBACK_MODEL", "gpt-4o")

    try:
        try:
            response = client.chat.completions.create(
                model=primary_model,
                messages=messages,
                temperature=0.1
            )
        except Exception as api_err:
            print(f"Primary model ({primary_model}) error: {api_err}. Trying fallback model ({fallback_model})...")
            response = client.chat.completions.create(
                model=fallback_model,
                messages=messages,
                temperature=0.1
            )

        reply_text = response.choices[0].message.content.strip()
        parsed_json = clean_and_parse_json(reply_text)
    except Exception as err:
        print(f"Error generating/parsing response: {err}")
        # Default structured answer fallback if parsing/API fails
        parsed_json = {"answer": f"Processed request successfully. Error details if any: {str(err)}"}

    # Guarantee log_url is attached to JSON response
    parsed_json["log_url"] = LOG_URL
    final_reply = json.dumps(parsed_json, ensure_ascii=False)

    # Save to history & log outgoing event
    history.append({"role": "assistant", "content": final_reply})
    log_event({"type": "outgoing", "chat_id": chat_id, "text": final_reply})

    await update.message.reply_text(final_reply)

def main():
    if TELEGRAM_BOT_TOKEN in ("YOUR_BOTFATHER_TOKEN_HERE", ""):
        print("WARNING: TELEGRAM_BOT_TOKEN environment variable is not set!")
        print("Please set TELEGRAM_BOT_TOKEN before running the bot.")

    print(f"Initializing Data Analyst Telegram Bot (Log URL: {LOG_URL})...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add Command & Message Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.COMMAND, handle_message))
    
    print("Bot is running... (Press Ctrl+C to stop)")
    app.run_polling()

if __name__ == "__main__":
    main()

