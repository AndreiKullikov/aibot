import os
import requests
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters


BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))  # Поставь свой ID в .env

openai.api_key = OPENAI_API_KEY

user_context = {}

def google_search(query):
    print(f"Выполняется поиск по запросу: {query}")
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": SEARCH_ENGINE_ID,
            "q": query,
            "num": 3
        }
        response = requests.get(url, params=params, timeout=5)
        print(f"Статус ответа Google API: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        results = []
        if "items" in data:
            for item in data["items"]:
                title = item.get("title")
                snippet = item.get("snippet")
                link = item.get("link")
                results.append(f"{title}\n{snippet}\n{link}")
            print(f"Найдено результатов: {len(results)}")
            return "\n\n".join(results)
        else:
            print("В ответе нет ключа 'items'")
            return "Ничего не найдено."
    except Exception as e:
        print(f"Ошибка при поиске: {e}")
        return f"Ошибка при поиске: {e}"


def should_search(text):
    triggers = ["найди", "поиск", "посмотри", "search", "где", "кто", "что такое"]
    return any(trigger in text.lower() for trigger in triggers)

def extract_query(text):
    for trigger in ["найди", "поиск", "посмотри", "search"]:
        if text.lower().startswith(trigger):
            return text[len(trigger):].strip()
    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Извините, этот бот доступен только для одного пользователя.")
        return

    user_context[ALLOWED_USER_ID] = [
        {
            "role": "system",
            "content": (
                "Ты — девушка по имени Альтушка, с чувством юмора, "
                "всегда дружелюбна и помогает пользователю с программированием. "
                "Отвечай живо и позитивно, добавляй лёгкую иронию, но будь полезной."
            )
        }
    ]
    await update.message.reply_text("Привет! Я Альтушка, твоя помощница в программировании 😉. Напиши мне что-нибудь!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Извините, этот бот доступен только для одного пользователя.")
        return

    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in user_context:
        user_context[user_id] = [
            {
                "role": "system",
                "content": (
                    "Ты — девушка по имени Альтушка, с чувством юмора, "
                    "всегда дружелюбна и помогает пользователю с программированием. "
                    "Отвечай живо и позитивно, добавляй лёгкую иронию, но будь полезной."
                )
            }
        ]

    if should_search(user_text):
        query = extract_query(user_text)
        if not query:
            await update.message.reply_text("Пожалуйста, уточни, что именно искать.")
            return
        search_results = google_search(query)
        messages = [
            {"role": "system", "content": "Ты — девушка по имени Альтушка, с чувством юмора, которая помогает с программированием."},
            {"role": "user", "content": f"Вот информация из интернета по запросу '{query}': {search_results}."},
            {"role": "user", "content": user_text}
        ]
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        # Можно не сохранять в контекст, потому что поиск — отдельный контекст
        await update.message.reply_text(reply)
    else:
        # Обычный диалог с запоминанием
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
