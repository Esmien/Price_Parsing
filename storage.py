import json
from models import Product # Импортируем нашу модель

class IOFile:
    def __init__(self, filename: str):
        self.filename = filename

    def write_file(self, products: list[Product]):
        """Сохраняет список продуктов в JSON"""
        try:
            # Превращаем список объектов Product в список словарей
            data_to_save = [p.to_dict() for p in products]
            
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Локальный бекап сохранен: {self.filename}")
        except Exception as e:
            print(f"❌ Ошибка сохранения файла: {e}")