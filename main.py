import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from keep_alive import keep_alive

user_keys = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to XPSMM Bot! Please send your API Key.")

async def save_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_keys[user_id] = update.message.text.strip()
    await update.message.reply_text("✅ API Key saved. Use /balance /order <id> /refill <id>")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    key = user_keys.get(uid)
    if not key:
        return await update.message.reply_text("Send API key first.")
    r = requests.post("https://xpsmm.com/api", data={"key": key, "action": "balance"}).json()
    await update.message.reply_text(f"💰 Balance: {r.get('balance')} {r.get('currency')}")

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    key = user_keys.get(uid)
    if not key or len(context.args) != 1:
        return await update.message.reply_text("Usage: /order <order_id>")
    r = requests.post("https://xpsmm.com/api", data={"key": key, "action": "status", "order": context.args[0]}).json()
    await update.message.reply_text(f"Status: {r.get('status')}\nRemains: {r.get('remains')}")

async def refill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    key = user_keys.get(uid)
    if not key or len(context.args) != 1:
        return await update.message.reply_text("Usage: /refill <order_id>")
    r = requests.post("https://xpsmm.com/api", data={"key": key, "action": "refill", "order": context.args[0]}).json()
    await update.message.reply_text(f"🔁 Refill ID: {r.get('refill')}")

def main():
    keep_alive()
    app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_key))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("order", order))
    app.add_handler(CommandHandler("refill", refill))
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
