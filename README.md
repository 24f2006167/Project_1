<div align="center">

# 📊 Data Analyst Telegram Bot

An intelligent, autonomous LLM agent built for the **IITM TDS Project 1 Assessment**.  
Capable of answering complex data analysis queries, chart interpretations, and statistical calculations with strictly structured JSON responses.

[![Telegram Bot](https://img.shields.io/badge/Telegram-@shitanshu__data__bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/shitanshu_data_bot)
[![Public Log](https://img.shields.io/badge/Public%20Log-run.jsonl-brightgreen?style=for-the-badge&logo=json)](https://raw.githubusercontent.com/24f2006167/Project_1/main/run.jsonl)
[![Python Version](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LLM Powered](https://img.shields.io/badge/LLM-AIPipe%20%2F%20OpenAI-FF6F61?style=for-the-badge&logo=openai&logoColor=white)](https://aipipe.org)

---

### 🔗 **Direct Telegram Link**: [t.me/shitanshu_data_bot](https://t.me/shitanshu_data_bot)

</div>

---

## 💡 Overview

This Telegram bot listens for data analysis prompts and replies with **exactly one valid JSON object** adhering strictly to the shape requested by the user prompt, along with a publicly accessible, `wget`-able audit log URL.

### 🌟 Key Features
- **🤖 Autonomous LLM Analysis**: Powered by `gpt-4o-mini` / `gpt-4o` via [AIPipe](https://aipipe.org) to handle natural language data queries.
- **⚡ Smart Fallback Solver**: Deterministic Regex & mathematical parser for instant state lookups (MOSPI, NFHS) and basic calculations.
- **🖼️ Multimodal Support**: Processes attached images, charts, and diagrams directly from Telegram messages.
- **📜 Live Audit Logging**: Automatically appends execution traces to [`run.jsonl`](https://raw.githubusercontent.com/24f2006167/Project_1/main/run.jsonl) and syncs with GitHub.

---

## 📥 Expected Output Format

The bot responds with **ONLY** a valid JSON payload:

```json
{
  "answer": {
    "state": "Assam"
  },
  "log_url": "https://raw.githubusercontent.com/24f2006167/Project_1/main/run.jsonl"
}
```

---

## 🚀 Quick Setup & Local Running

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file or export your tokens:
```bash
export TELEGRAM_BOT_TOKEN="8740152123:AAH7z32zQpmeNR3rVpZjeCEqo0ZXDMaHmG8"
export AIPIPE_TOKEN="YOUR_AIPIPE_TOKEN"
export LOG_URL="https://raw.githubusercontent.com/24f2006167/Project_1/main/run.jsonl"
```

### 3. Launch the Bot
```bash
python bot.py
```

---

## 🧪 Testing with Official Grading Harness

Clone and execute the evaluation suite against the bot:

```bash
git clone https://github.com/Jivraj-18/tds-p1-t2-2026-telegram-bot eval_harness
cd eval_harness
```

Run test suite commands:
```bash
python generate.py
python collect.py
python grade.py
```

---

## 📦 Deployment & 24/7 Hosting

The bot includes an embedded health-check HTTP server for **Render / Railway / Koyeb** deployment:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python bot.py`
- **Environment Variables**: Add `TELEGRAM_BOT_TOKEN`, `AIPIPE_TOKEN`, and `LOG_URL`.

---

## 📝 Exam Portal Submission Details

```text
https://github.com/24f2006167/Project_1, shitanshu_data_bot
```
