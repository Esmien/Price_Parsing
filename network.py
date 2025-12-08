import requests
import gspread
from gspread.exceptions import WorksheetNotFound
from config import USER_AGENT
from models import Product

class TelegramClient:
    """Отвечает только за скачивание HTML"""
    def __init__(self):
        self.headers = {'User-Agent': USER_AGENT} # инициализирует типа браузер

    def fetch_html(self, url: str) -> str | None: 
        try:
            response = requests.get(url, headers=self.headers) # пытается получить html-страницу, прикинувшись браузером
            # Принудительно ставим UTF-8 для эмодзи
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                return response.text # если ответ был получен со статусом 200(ок), то возвращает html-код страницы
            print(f"❌ Ошибка сервера Telegram: {response.status_code} для {url}")
        except requests.RequestException as e:
            print(f"❌ Ошибка сети при скачивании {url}: {e}")
        return None


class GoogleSheetsClient:
    """Отвечает за работу с таблицами Google"""
    def __init__(self, credentials_file: str, spreadsheet_title: str):
        self.credentials_file = credentials_file
        self.spreadsheet_title = spreadsheet_title
        self.client = None
        self.sh = None # Сама таблица (книга)

    def connect(self):
        """Авторизация и открытие книги"""
        try:
            self.client = gspread.service_account(filename=self.credentials_file) # инициализируем доступ к апи(пользователя)
            self.sh = self.client.open(self.spreadsheet_title) # открываем таблицу
            print(f"✅ Подключено к таблице: '{self.spreadsheet_title}'")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения к Google Sheets: {e}")
            return False

    def update_sheet(self, sheet_name: str, products: list[Product]) -> None:
        """
        Обновляет данные на КОНКРЕТНОМ листе.
        Если листа нет — создает его.
        :param sheet_name: название ЛИСТА в таблице
        :param products: список экземпляров датакласса(один экземпляр - 1 позиция в прайсе)
        """
        if not self.sh: # если таблицу открыть не вышло
            print("⚠️ Нет соединения с таблицей.")
            return

        # 1. Пытаемся получить лист, или создаем новый
        try:
            worksheet = self.sh.worksheet(sheet_name) # пробует прочитать лист с указанным именем
        except WorksheetNotFound:
            print(f"ℹ️ Лист '{sheet_name}' не найден. Создаю новый...")
            worksheet = self.sh.add_worksheet(title=sheet_name, rows=1000, cols=10) # создает лист с именем на 10 столбцов и 1000 строк

        # 2. Готовим данные
        # Заголовок
        rows = [['Название', 'Цена', 'Флаг', 'Комментарий']]
        # Данные (используем наш метод to_row из models.py)
        for p in products: # перебирает записи в прайс(уже чистые)
            rows.append(p.to_row()) #добавляет в список строк списковое представление записи(метод датакласса)

        try:
            # 3. Очищаем лист и пишем заново
            worksheet.clear()
            worksheet.update(values=rows, range_name='A1')
            
            # 4. Наводим красоту (жирный шрифт заголовка)
            worksheet.format('A1:D1', {'textFormat': {'bold': True}})
            
            print(f"✅ Лист '{sheet_name}' обновлен! Записано строк: {len(rows)}")
            
        except Exception as e:
            print(f"❌ Ошибка при записи на лист '{sheet_name}': {e}")