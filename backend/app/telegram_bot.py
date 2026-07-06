import logging
from datetime import date
from typing import Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app import db, claude_client
from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from app.feeds.synthesis import run_daily_synthesis

logger = logging.getLogger("niche.telegram")

_application: Optional[Application] = None


def _format_summary(s: dict) -> str:
    return f"• {s['headline']}\n  {s['summary']}\n  ({s['source_label']})"


async def notify(text: str):
    if not _application or not TELEGRAM_CHAT_ID:
        logger.info("Telegram not configured, skipping notify: %s", text[:80])
        return
    await _application.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)


async def cmd_digest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    research_items = db.get_summaries(feed="research", since_hours=24, limit=5)
    market_items = db.get_summaries(feed="market", since_hours=24, limit=5)
    lines = ["Research:"] + [_format_summary(s) for s in research_items]
    lines += ["", "Market intel:"] + [_format_summary(s) for s in market_items]
    await update.message.reply_text("\n".join(lines) or "Nothing new yet.")


async def cmd_research(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = db.get_summaries(feed="research", since_hours=24, limit=10)
    text = "\n\n".join(_format_summary(s) for s in items) or "Nothing new yet."
    await update.message.reply_text(text)


async def cmd_market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = db.get_summaries(feed="market", since_hours=24, limit=10)
    text = "\n\n".join(_format_summary(s) for s in items) or "Nothing new yet."
    await update.message.reply_text(text)


async def cmd_investors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    investors = db.get_investors(days=30)
    if not investors:
        await update.message.reply_text("No investors mentioned in the last 30 days.")
        return
    lines = [f"{i['name']} — {i['mentions']} mention(s)" for i in investors]
    await update.message.reply_text("\n".join(lines))


async def cmd_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = date.today().isoformat()
    idea = db.get_niche_idea(today)
    if idea is None:
        if not claude_client.is_configured():
            await update.message.reply_text(
                "Niche Ideas needs an ANTHROPIC_API_KEY to cross-reference the feeds — not set yet."
            )
            return
        await update.message.reply_text("Generating today's idea, one moment...")
        result = run_daily_synthesis()
        if result is None:
            await update.message.reply_text("Not enough new items in the last 24h to synthesize an idea.")
            return
        await update.message.reply_text(result["idea_text"])
        return
    await update.message.reply_text(idea["idea_text"])


async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    note_text = " ".join(context.args)
    if not note_text:
        await update.message.reply_text("Usage: /add <note>")
        return
    db.insert_note(note_text)
    await update.message.reply_text("Logged.")


def build_application() -> Application:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("digest", cmd_digest))
    app.add_handler(CommandHandler("research", cmd_research))
    app.add_handler(CommandHandler("market", cmd_market))
    app.add_handler(CommandHandler("investors", cmd_investors))
    app.add_handler(CommandHandler("idea", cmd_idea))
    app.add_handler(CommandHandler("add", cmd_add))
    return app


async def start_bot():
    global _application
    _application = build_application()
    await _application.initialize()
    await _application.start()
    await _application.updater.start_polling()


async def stop_bot():
    global _application
    if _application is None:
        return
    await _application.updater.stop()
    await _application.stop()
    await _application.shutdown()
    _application = None
