# Setup Guide: Autonomous AI Builder Agent

Follow these exact steps to deploy the agent so it runs automatically without your intervention.

## 1. Create the GitHub Repository

1. Go to your GitHub account and create a **New Repository**.
2. Name it something like `daily-ai-builds`.
3. Set it to **Public** or **Public** (recommended Public so you can share your progress).
4. Do NOT initialize it with a README, .gitignore, or license (leave it completely empty).
5. Open your terminal in the `Auto GB AI Agent` folder locally and run:
   ```bash
   git init
   git add .
   git commit -m "Initial agent setup"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/daily-ai-builds.git
   git push -u origin main
   ```

## 2. Get the Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Create a new API key.
3. Save it to your clipboard (you will need it for GitHub Secrets).

## 3. Create the Telegram Bot via @BotFather

1. Open Telegram and search for `@BotFather`.
2. Send the command `/newbot`.
3. Choose a name and a username (must end in `bot`).
4. BotFather will give you an **HTTP API Token**. Save it.
5. To get your **Chat ID**, search for `@userinfobot` or `@RawDataBot` on Telegram, send a message, and write down the `id` field from the response.

## 4. Add GitHub Secrets

1. Go to your GitHub repository in the browser.
2. Click **Settings** ➔ **Secrets and variables** ➔ **Actions**.
3. Create the following "New repository secrets":
   - `GEMINI_API_KEY`: Paste your Gemini key.
   - `TELEGRAM_TOKEN`: Paste your Telegram bot token.
   - `TELEGRAM_CHAT_ID`: Paste your Chat ID.

## 5. Configure `config.json`

Open `config.json` in this repo and update the `github_username` and `github_repo` fields to match your actual GitHub username and repo name. *You do not need to paste your API keys into `config.json` since they will be securely read from GitHub Secrets.* Commit and push this change to GitHub.

## 6. Do the First Manual Run to Test

You can manually trigger the bot to make sure it works before tomorrow!

1. Go to your GitHub repository in the browser.
2. Click the **Actions** tab.
3. Under "All workflows" on the left, click **Daily AI Builder**.
4. Click the **Run workflow** dropdown on the right and click **Run workflow**. 
5. Wait ~30-60 seconds. You should get a Telegram message, and your project will correctly appear in the repository!

> Note: To run the Telegram Bot polling to access commands like `/status` and `/history`, you need to host `telegram_bot.py` on a long-running server (like Railway, Heroku, or a VPS) OR run it locally in the background. The daily generation itself requires 0 servers, entirely handled by GitHub Actions.
