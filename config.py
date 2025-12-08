import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# --- Настройки Google ---
# Имя файла с ключами (лежит в корне)
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE', 'credentials.json')

# Общее название Google Таблицы (Файла), куда будем всё писать
SPREADSHEET_TITLE = os.getenv('SPREADSHEET_TITLE', 'ApplePrices')

# --- Источники данных ---
# Формат: { "Название Листа": "Ссылка на пост" }
# Ты можешь добавлять сюда сколько угодно ссылок
URL_MAP = {
    "Huawei": "https://t.me/BigSaleApple/11193?embed=1",
    "Samsung": "https://t.me/BigSaleApple/11198?embed=1", # Пример второй ссылки
    # "Xiaomi": "https://t.me/...",
}

# User-Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'