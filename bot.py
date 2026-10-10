
import os
import json
import asyncio
from pathlib import Path
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes
)

TOKEN = os.environ["BOT_TOKEN"]
FILE = Path("history.json")


def get_history():
    if FILE.exists():
        try:
            return json.loads(FILE.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass
    return []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 DK Wine Smart Assistant\n\n"
        "/timer - ৩০ সেকেন্ড টাইমার\n"
        "/result BIG - BIG ফলাফল সংরক্ষণ\n"
        "/result SMALL - SMALL ফলাফল সংরক্ষণ\n"
        "/history - ফলাফলের হিস্ট্রি\n"
        "/predict - পরীক্ষামূলক বিশ্লেষণ"
    )


async def timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏱️ ৩০ সেকেন্ড শুরু!")
    for seconds in range(29, -1, -1):
        await asyncio.sleep(1)
        try:
            await msg.edit_text(f"⏱️ বাকি {seconds} সেকেন্ড")
        except Exception:
            pass
    await msg.edit_text("🔔 সময় শেষ!")


async def result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or context.args[0].upper() not in ("BIG", "SMALL"):
        await update.message.reply_text(
            "ব্যবহার: /result BIG অথবা /result SMALL"
        )
        return

    records = get_history()
    records.append({
        "result": context.args[0].upper()
    })
    FILE.write_text(
        json.dumps(records[-200:], ensure_ascii=False),
        encoding="utf-8"
    )
    await update.message.reply_text("✅ ফলাফল সংরক্ষিত হয়েছে।")


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    records = get_history()
    if not records:
        await update.message.reply_text("এখনো কোনো ফলাফল নেই।")
        return

    lines = [r["result"] for r in records[-20:]]
    await update.message.reply_text(
        "📋 শেষ ফলাফল:\n" + "\n".join(reversed(lines))
    )


async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    records = get_history()
    if not records:
        await update.message.reply_text(
            "আগে /result BIG অথবা /result SMALL দিয়ে ফলাফল যোগ করুন।"
        )
        return

    big = sum(r["result"] == "BIG" for r in records[-10:])
    small = sum(r["result"] == "SMALL" for r in records[-10:])
    await update.message.reply_text(
        f"📊 শেষ ১০টি রেকর্ডে BIG: {big}, SMALL: {small}\n"
        "এটি অতীতের হিসাব, পরের রাউন্ডের নিশ্চিত ভবিষ্যদ্বাণী নয়।"
    )


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("timer", timer))
    app.add_handler(CommandHandler("result", result))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("predict", predict))
    app.run_polling()


if __name__ == "__main__":
    main()
