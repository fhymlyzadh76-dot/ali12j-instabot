import os
import asyncio
import tempfile
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\n"
        "لینک عمومی پست یا ریلز اینستاگرام را بفرست."
    )

def download_instagram(url, folder):
    opts = {
        "outtmpl": os.path.join(folder, "%(title).80s.%(ext)s"),
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)

        filename = ydl.prepare_filename(info)
        path = Path(filename)

        return path if path.exists() else None

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = (update.message.text or "").strip()

    if "instagram.com" not in url.lower():
        await update.message.reply_text(
            "لطفاً لینک عمومی اینستاگرام بفرست."
        )
        return

    msg = await update.message.reply_text("⏳ در حال دانلود...")

    with tempfile.TemporaryDirectory() as folder:
        try:
            path = await asyncio.to_thread(
                download_instagram, url, folder
            )

            if not path:
                await msg.edit_text("❌ فایل پیدا نشد.")
                return

            with path.open("rb") as f:
                await update.message.reply_video(
                    video=f,
                    caption="✅ آماده شد"
                )

            await msg.delete()

        except Exception:
            await msg.edit_text(
                "❌ دانلود انجام نشد. ممکن است لینک خصوصی یا نامعتبر باشد."
            )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)
    )

    app.run_polling()

if __name__ == "__main__":
    main()
