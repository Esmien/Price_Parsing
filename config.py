import os
from dotenv import load_dotenv
from pathlib import Path

# Загружаем .env
load_dotenv()

# --- Настройки Google ---
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
SPREADSHEET_TITLE = os.getenv('SPREADSHEET_TITLE')

# --- Настройки Парсера ---
# {"Имя Листа": ["Ссылки"]}
URL_MAP = {
    "Huawei": [
        "https://t.me/BigSaleApple/11193?embed=1"
    ],
    
    "Samsung": [
        "https://t.me/BigSaleApple/11198?embed=1",
    ],
    
    "iPhone": [
        "https://t.me/BigSaleApple/12462?embed=1", # 13
        "https://t.me/BigSaleApple/12463?embed=1", # 14 серия
        "https://t.me/BigSaleApple/12464?embed=1", # 15 серия
        "https://t.me/BigSaleApple/12465?embed=1", # 16
        "https://t.me/BigSaleApple/12466?embed=1", # 16 Pro
        "https://t.me/BigSaleApple/12469?embed=1", # 17
        "https://t.me/BigSaleApple/12470?embed=1", # Air
        "https://t.me/BigSaleApple/12471?embed=1", # 17 Pro
        
    ]
}

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

BACKUP_DIR = Path('storage')
BACKUP_DIR.mkdir(exist_ok=True)