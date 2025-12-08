from dataclasses import dataclass

@dataclass
class Product:
    """Модель данных товара"""
    name: str
    price: int
    flag: str
    comment: str

    def __str__(self):
        return f"{self.flag:<5} | {self.name[:40]:<40} | {self.price:<8} | {self.comment}"
    
    def to_dict(self):
        """Удобный метод для конвертации в словарь (для JSON)"""
        return {
            'name': self.name,
            'price': self.price,
            'flag': self.flag,
            'comment': self.comment
        }
    
    def to_row(self):
        """Удобный метод для конвертации в строку таблицы (для Google Sheets)"""
        return [self.name, self.price, self.flag, self.comment]