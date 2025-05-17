import os
import requests
import openai
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)
logging.getLogger("telegram").setLevel(logging.DEBUG)

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))

openai.api_key = OPENAI_API_KEY

# Функция поиска через Google Custom Search API
def google_search(query: str) -> str:
    logger.info(f"Выполняется поиск по запросу: '{query}'")
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": SEARCH_ENGINE_ID,
            "q": query,
            "num": 3
        }
        response = requests.get(url, params=params, timeout=5)
        logger.info(f"Ответ Google API, статус: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        if "items" not in data:
            logger.info("В ответе Google API нет 'items'")
            return "Ничего не найдено."
        results = []
        for item in data["items"]:
            title = item.get("title", "Без заголовка")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            results.append(f"{title}\n{snippet}\n{link}")
        logger.info(f"Найдено результатов: {len(results)}")
        return "\n\n".join(results)
    except Exception as e:
        logger.error(f"Ошибка при поиске: {e}")
        return f"Ошибка при поиске: {e}"

def should_search(text: str) -> bool:
    triggers = ["найди", "поиск", "посмотри", "search", "где", "кто", "что такое"]
    result = any(trigger in text.lower() for trigger in triggers)
    logger.info(f"Проверка триггеров для поиска: {result} (сообщение: '{text}')")
    return result

def extract_query(text: str) -> str:
    for trigger in ["найди", "поиск", "посмотри", "search"]:
        if text.lower().startswith(trigger):
            query = text[len(trigger):].strip()
            logger.info(f"Извлечён запрос для поиска: '{query}'")
            return query
    logger.info(f"Запрос для поиска не изменён: '{text}'")
    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"/start вызван пользователем {user_id}")
    if user_id != ALLOWED_USER_ID:
        logger.warning(f"Пользователь {user_id} не разрешён для использования бота.")
        await update.message.reply_text("Извините, этот бот доступен только для одного пользователя.")
        return
    await update.message.reply_text("Привет! Я Альтушка, твоя помощница с программированием и поиском в интернете 😉. Напиши мне что-нибудь!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    logger.info(f"handle_message вызван пользователем {user_id}, сообщение: '{user_text}'")

    if user_id != ALLOWED_USER_ID:
        logger.warning(f"Пользователь {user_id} не разрешён.")
        await update.message.reply_text("Извините, этот бот доступен только для одного пользователя.")
        return

    if should_search(user_text):
        query = extract_query(user_text)
        if not query:
            await update.message.reply_text("Пожалуйста, уточни, что именно искать.")
            return
        search_results = google_search(query)
        messages = [
            {
                "role": "system",
                "content": (
                    "Ты — дружелюбный и информативный помощник с чувством юмора. "
                    "Твоя задача — ответить на вопросы пользователя, используя данные, которые я предоставлю."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Ниже приведена информация, найденная в интернете по запросу '{query}':\n"
                    f"{search_results}\n\n"
                    "Пожалуйста, составь ответ пользователю, опираясь на эти данные, без отсылок к тому, что ты не можешь ответить."
                )
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
            )
            reply = response.choices[0].message.content
            logger.info(f"Ответ OpenAI с учётом поиска: {reply}")
        except Exception as e:
            logger.error(f"Ошибка OpenAI: {e}")
            reply = f"Произошла ошибка при обращении к OpenAI: {e}"
        await update.message.reply_text(reply)
    else:
        # Для обычных вопросов без триггера — просто отвечаем через OpenAI
        messages = [
            {
                "role": "system",
                "content": (
                    "Ты — дружелюбный и информативный помощник с чувством юмора, "
                    "помогающий с программированием и другими вопросами."
                )
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
            )
            reply = response.choices[0].message.content
            logger.info(f"Ответ OpenAI без поиска: {reply}")
        except Exception as e:
            logger.error(f"Ошибка OpenAI: {e}")
            reply = f"Произошла ошибка при обращении к OpenAI: {e}"
        await update.message.reply_text(reply)

def main():
    logger.info("Бот запускается...")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
