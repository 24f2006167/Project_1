# Q5 - Data Analyst Telegram Bot

A Telegram Bot built for the TDS P1 Assessment that answers data analysis questions using an LLM via [AIPipe](https://aipipe.org) and logs all runs to a publicly accessible `run.jsonl` file.

👉 **Direct Telegram Bot Link**: [https://t.me/shitanshu_data_bot](https://t.me/shitanshu_data_bot) (`@shitanshu_data_bot`)

---

## 🚀 Quick Setup & Local Running

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   export TELEGRAM_BOT_TOKEN="YOUR_BOTFATHER_TOKEN"
   export AIPIPE_TOKEN="eyJhbGciOiJIUzI1NiJ9..."
   export LOG_URL="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/run.jsonl"
   ```

3. **Start the Bot**:
   ```bash
   python bot.py
   ```

---

## 🧪 Testing with the Official Grading Harness

Clone and run the official evaluation pipeline against your bot:

```bash
git clone https://github.com/Jivraj-18/tds-p1-t2-2026-telegram-bot eval_harness
cd eval_harness
```

Run test suite commands following the harness documentation:
- `python generate.py`
- `python collect.py`
- `python grade.py`

---

## 📦 Deployment (24/7 Hosting)

Deploy your bot to a cloud platform so it remains online 24/7:
- **Render** / **Railway** / **Koyeb**: Create a Background Worker connected to your GitHub repository.
  - **Start Command**: `python bot.py`
  - **Environment Variables**: Add `TELEGRAM_BOT_TOKEN`, `AIPIPE_TOKEN`, and `LOG_URL`.

---

## 📝 Registration Format

In the exam portal answer box, submit your GitHub repository link and bot username separated by a comma:

```
https://github.com/YOUR_USERNAME/YOUR_REPO, your_bot_username
```
