# Telegram Bot with OpenAI GPT-3.5

Этот проект — Telegram-бот на Python, который отвечает пользователям с помощью модели OpenAI GPT-3.5.  
Бот написан с использованием библиотеки `python-telegram-bot` версии 20+ и использует polling для получения сообщений.

---

## 🔧 Возможности

- 🤖 Ответы на сообщения пользователей с помощью OpenAI GPT-3.5  
- 🛠 Команда `/start` для приветствия пользователя  
- ⚙️ Простая и удобная настройка через `.env` файл  
- 🐳 Запуск локально и в Docker контейнере  

---

## 📦 Требования

- Python 3.10 или выше  
- Ключ API OpenAI ([получить здесь](https://platform.openai.com/account/api-keys))  
- Токен Telegram-бота (создается через [@BotFather](https://t.me/BotFather))  
- Docker (опционально, для контейнеризации)  

---

## 📁 Структура проекта

```
my_telegram_bot/
├── .gitignore           # Файлы и папки, игнорируемые Git
├── .env.example         # Пример файла с переменными окружения
├── Dockerfile           # Конфигурация Docker-образа
├── README.md            # Этот файл с описанием проекта
├── requirements.txt     # Зависимости Python
└── bot.py               # Основной скрипт бота
```

---

## 🚀 Установка и запуск локально

1. Клонируйте репозиторий:

```bash
git clone https://github.com/yourusername/my_telegram_bot.git
cd my_telegram_bot
```

2. Создайте файл `.env` на основе шаблона и заполните своими ключами:

```bash
cp .env.example .env
```

3. Отредактируйте `.env`, указав значения:

```ini
BOT_TOKEN=ваш_токен_бота
OPENAI_API_KEY=ваш_ключ_openai
```

4. Установите зависимости:

```bash
pip install -r requirements.txt
```

5. Запустите бота:

```bash
python bot.py
```

6. В Telegram найдите своего бота, отправьте команду `/start`, а затем любое сообщение.

---

## 🐳 Запуск в Docker

1. Соберите Docker-образ:

```bash
docker build -t mytelegrambot .
```

2. Запустите контейнер с передачей переменных окружения из `.env`:

```bash
docker run --env-file .env mytelegrambot
```

---

## 💬 Как использовать

- Отправьте команду `/start` — бот поприветствует вас.  
- Напишите любое сообщение — бот ответит, сгенерировав ответ с помощью OpenAI.

---

