from config import URL_MAP, SPREADSHEET_TITLE, CREDENTIALS_FILE, BACKUP_DIR
from network import TelegramClient, GoogleSheetsClient
from parsing import TextExtractor, PriceParser
from storage import IOFile

class App:
    def __init__(self):
        self.tg_client = TelegramClient()
        self.gs_client = GoogleSheetsClient(CREDENTIALS_FILE, SPREADSHEET_TITLE)
        
        self.extractor = TextExtractor()
        self.parser = PriceParser()

    def run(self):
        print(f"🚀 Запуск парсера")
        print(f"📄 Целевая таблица: {SPREADSHEET_TITLE}")
        
        is_gs_connected = self.gs_client.connect()
        
        # Перебираем бренды (Листы)
        for sheet_name, urls_list in URL_MAP.items():
            print(f"\n--- 📱 Обработка категории: {sheet_name} ---")
            
            # Создаем общий список товаров для ЭТОЙ категории (листа)
            category_products = []
            
            # Если в конфиге случайно написали строку вместо списка, превращаем в список
            if isinstance(urls_list, str):
                urls_list = [urls_list]

            # Бежим по всем ссылкам для этого листа
            for i, url in enumerate(urls_list, 1):
                print(f"   🔗 Скачивание части {i}/{len(urls_list)}...")
                
                html = self.tg_client.fetch_html(url)
                if not html:
                    print("      ⏭️ Ошибка загрузки, пропускаем.")
                    continue

                text = self.extractor.html_to_text(html)
                if not text:
                    print("      ⏭️ Пустой текст, пропускаем.")
                    continue

                products = self.parser.parse(text)
                print(f"      📦 Найдено товаров: {len(products)}")
                
                # Добавляем найденное в общий котел категории
                category_products.extend(products)

            # ИТОГ ПО КАТЕГОРИИ
            if category_products:
                print(f"✅ Итого для '{sheet_name}': {len(category_products)} позиций.")
                
                # 1. Сохраняем JSON (Samsung.json будет содержать всё сразу)
                json_filename = BACKUP_DIR / f"{sheet_name}.json"
                IOFile(json_filename).write_file(category_products)
                
                # 2. Отправляем в Google (на ОДИН лист все сразу)
                if is_gs_connected:
                    self.gs_client.update_sheet(sheet_name, category_products)
            else:
                print(f"⚠️ Категория '{sheet_name}' пуста.")

        print("\n✅ Работа завершена!")

if __name__ == '__main__':
    app = App()
    app.run()
