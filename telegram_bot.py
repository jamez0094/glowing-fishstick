import os
import json
import requests
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ==========================================
# SYNCHRONOUS NOTIFICATION FUNCTIONS (Used by agent.py)
# ==========================================

def get_telegram_creds(config):
    token = os.environ.get("TELEGRAM_TOKEN", config.get("telegram_token"))
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", config.get("telegram_chat_id"))
    return token, chat_id

def send_message_sync(token, chat_id, text):
    if not token or not chat_id or token == "YOUR_TELEGRAM_BOT_TOKEN":
        print("Telegram not configured. Skipping notification.")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Telegram notification sent.")
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")

def send_build_notification(config, day, name, difficulty, stack, repo_url, progress_info):
    token, chat_id = get_telegram_creds(config)
    
    msg = f"""🚀 <b>Day {day} — {name}</b>
━━━━━━━━━━━━━━━━━━━━━━━━
🎯 <b>Level:</b>   {difficulty}
⚡ <b>Stack:</b>   {stack}
🔗 <a href="{repo_url}">GitHub Repo Link</a>
━━━━━━━━━━━━━━━━━━━━━━━━
⏭️ {progress_info['projects_to_next']} more projects → {progress_info['next_level']}
<code>{progress_info['progress_bar']}</code>"""
    
    send_message_sync(token, chat_id, msg)

def send_failure_notification(config, error_message):
    token, chat_id = get_telegram_creds(config)
    msg = f"❌ <b>Daily AI Build Failed</b>\n\n<code>{error_message}</code>"
    send_message_sync(token, chat_id, msg)

def send_levelup_notification(config, new_level):
    token, chat_id = get_telegram_creds(config)
    msg = f"🎉 <b>LEVEL UP!</b>\n\nYou are now at the <b>{new_level}</b> level! Projects will now be more complex."
    send_message_sync(token, chat_id, msg)

def send_milestone_notification(config, day, milestone_type):
    token, chat_id = get_telegram_creds(config)
    if milestone_type == "streak":
        msg = f"🔥 <b>STREAK MILESTONE</b>\n\nYou've reached a {day} day continuous building streak!"
    else:
        msg = f"🏆 <b>BIG MILESTONE</b>\n\nCongratulations on reaching Day {day}!"
    send_message_sync(token, chat_id, msg)


# ==========================================
# ASYNCHRONOUS BOT COMMANDS (Run independently)
# ==========================================

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

def load_history():
    try:
        with open("past_projects.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history = load_history()
    if not history:
        await update.message.reply_text("No projects built yet.")
        return
    last = history[-1]
    msg = f"Last build (Day {last['day']}):\n{last['name']} ({last['difficulty']})"
    await update.message.reply_text(msg)

async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history = load_history()
    day = len(history)
    # Import here to avoid circular dependencies if we ever import from this file
    import progression 
    info = progression.get_progress_info(day)
    msg = f"""🎯 Current Level: {info['current_level']}
⏭️ Next: {info['next_level']} in {info['projects_to_next']} projects
<code>{info['progress_bar']}</code>"""
    await update.message.reply_text(msg, parse_mode="HTML")

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    past = load_history()
    recent = past[-7:]
    if not recent:
        await update.message.reply_text("No history available.")
        return
    msg = "<b>Recent Projects:</b>\n"
    for p in recent:
        msg += f"• Day {p['day']}: {p['name']}\n"
    await update.message.reply_text(msg, parse_mode="HTML")

async def streak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history = load_history()
    msg = f"🔥 Current Streak: {len(history)} days"
    await update.message.reply_text(msg)

async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = load_config()
    config["paused"] = True
    save_config(config)
    await update.message.reply_text("⏸️ Agent is paused. Will skip tomorrow's build.")

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = load_config()
    config["paused"] = False
    save_config(config)
    await update.message.reply_text("▶️ Agent is resumed. Daily builds restored.")

async def forcebuild(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Triggering manual build... Please check GitHub Actions or the logs.")
    # In a full deployment, this might trigger the GitHub Action API.
    # For local script, we can run it as a subprocess.
    try:
        subprocess.Popen(["python", "agent.py"])
    except Exception as e:
        await update.message.reply_text(f"Error starting build: {e}")

async def stack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = load_config()
    langs = ", ".join(config.get("languages", []))
    styles = ", ".join(config.get("styling", []))
    await update.message.reply_text(f"⚡ Current Stack:\nLanguages: {langs}\nStyling: {styles}")

async def addstack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /addstack [technology]")
        return
    tech = " ".join(args)
    config = load_config()
    config.setdefault("languages", []).append(tech)
    save_config(config)
    await update.message.reply_text(f"✅ Added {tech} to stack!")

async def removestack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /removestack [technology]")
        return
    tech = " ".join(args)
    config = load_config()
    if "languages" in config and tech in config["languages"]:
        config["languages"].remove(tech)
        save_config(config)
        await update.message.reply_text(f"🗑️ Removed {tech} from stack!")
    else:
        await update.message.reply_text(f"⚠️ {tech} not found in current languages stack.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmds = """Available cmds:
/status - today's build info
/progress - current level + progress bar
/history - last 7 projects built
/streak - current day streak
/pause - skip tomorrow's build
/resume - turn the agent back on
/forcebuild - trigger a build right now
/stack - see current tech stack
/addstack - add tech
/removestack - remove tech
/help - list this menu"""
    await update.message.reply_text(cmds)

def main():
    config = load_config()
    token = config.get("telegram_token")
    if token == "YOUR_TELEGRAM_BOT_TOKEN":
        print("Please configure your telegram_token in config.json")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("streak", streak))
    app.add_handler(CommandHandler("pause", pause))
    app.add_handler(CommandHandler("resume", resume))
    app.add_handler(CommandHandler("forcebuild", forcebuild))
    app.add_handler(CommandHandler("stack", stack))
    app.add_handler(CommandHandler("addstack", addstack))
    app.add_handler(CommandHandler("removestack", removestack))
    app.add_handler(CommandHandler("help", help_cmd))

    print("Telegram bot polling started...")
    app.run_polling()

if __name__ == '__main__':
    main()
