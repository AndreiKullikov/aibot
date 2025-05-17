import os
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID"))


openai.api_key = OPENAI_API_KEY

user_context = {}



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Извините, этот бот доступен только для одного пользователя.")
        return
    user_context[ALLOWED_USER_ID] = [
        {"role": "system", "content": "Ты умный помощник, говорящий по-русски."}
    ]
    await update.message.reply_text("Привет! Я бот GPT-4, готов помочь.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Извините, этот бот доступен только для одного пользователя.")
        return

    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in user_context:
        user_context[user_id] = [
            {"role": "system", "content": "Ты умный помощник, говорящий по-русски."}
        ]

    user_context[user_id].append({"role": "user", "content": user_text})

    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=user_context[user_id],
        temperature=0.7,
    )

    reply = response.choices[0].message.content
    user_context[user_id].append({"role": "assistant", "content": reply})

    await update.message.reply_text(reply)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
