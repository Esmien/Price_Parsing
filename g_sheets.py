import gspread

# --- 6. Работа с Google Таблицами (Export Layer) ---
class GoogleSheetsClient:
    def __init__(self, credentials_file: str, spreadsheet_name: str):
        self.credentials_file = credentials_file
        self.spreadsheet_name = spreadsheet_name
        self.client = None
        self.sheet = None

    def connect(self):
        """Авторизация и открытие таблицы"""
        try:
            # Подключаемся с помощью скачанного JSON ключа
            self.client = gspread.service_account(filename=self.credentials_file)
            # Открываем таблицу по названию (должно точно совпадать!)
            self.sh = self.client.open(self.spreadsheet_name)
            # Берем первый лист
            self.sheet = self.sh.sheet1
            print(f"✅ Успешное подключение к таблице: {self.spreadsheet_name}")
        except Exception as e:
            print(f"❌ Ошибка подключения к Google Sheets: {e}")
            print("Проверь: 1. Имя файла credentials.json. 2. Доступ бота к таблице (Share).")

    def update_data(self, products: list):
        """Полная перезапись данных в таблице"""
        if not self.sheet:
            print("Сначала нужно подключиться (connect)!")
            return

        # 1. Готовим данные: Превращаем список объектов Product в список списков
        # Заголовок
        rows = [['Название', 'Цена', 'Флаг', 'Комментарий']]
        
        # Данные
        for p in products:
            rows.append([
                p.name,
                p.price,
                p.flag,
                p.comment
            ])

        try:
            # 2. Очищаем лист
            self.sheet.clear()
            
            # 3. Заливаем новые данные (update принимает диапазон, A1 - старт)
            self.sheet.update(range_name='A1', values=rows)
            
            # (Опционально) Немного красоты: форматирование заголовка
            self.sheet.format('A1:D1', {'textFormat': {'bold': True}})
            
            print(f"✅ Данные успешно обновлены! Записано строк: {len(rows)}")
        except Exception as e:
            print(f"❌ Ошибка при записи данных: {e}")