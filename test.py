import requests
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional, List

# --- 1. Структура данных (Data Layer) ---
@dataclass
class Product:
    name: str
    price: int
    flag: str
    comment: str

    def __str__(self):
        """Красивый вывод для консоли"""
        return f"{self.flag:<5} | {self.name[:40]:<40} | {self.price:<8} | {self.comment}"

# --- 2. Работа с сетью (Network Layer) ---
class TelegramClient:
    def __init__(self, user_agent: str = 'Mozilla/5.0'):
        self.headers = {'User-Agent': user_agent}

    def fetch_html(self, url: str) -> Optional[str]:
        try:
            response = requests.get(url, headers=self.headers)
            response.encoding = 'utf-8'  # Критично для эмодзи
            if response.status_code == 200:
                return response.text
            print(f"Ошибка сервера: {response.status_code}")
        except requests.RequestException as e:
            print(f"Ошибка сети: {e}")
        return None

# --- 3. Обработка текста (Processing Layer) ---
class TextExtractor:
    @staticmethod
    def html_to_text(html: str) -> Optional[str]:
        """Извлекает текст из виджета, сохраняя структуру строк."""
        soup = BeautifulSoup(html, 'lxml')
        div = soup.find('div', class_='tgme_widget_message_text')
        
        if not div:
            return None
            
        # Заменяем <br> на переносы для корректного сплита
        for br in div.find_all('br'):
            br.replace_with('\n')
            
        return div.get_text(separator='\n', strip=True)

    @staticmethod
    def convert_emoji_to_latin(text: str) -> str:
        """Превращает Unicode-флаг (🇦🇪) в код (AE)."""
        match = re.search(r'[\U0001F1E6-\U0001F1FF]{2}', text)
        if match:
            flag_char = match.group(0)
            # Магия Unicode: ord(char) - offset = ASCII char
            return "".join([chr(ord(c) - 127397) for c in flag_char])
        return ""

# --- 4. Бизнес-логика парсинга (Logic Layer) ---
class PriceParser:
    def parse(self, raw_text: str) -> List[Product]:
        lines = raw_text.split('\n')
        products = []
        pending_flag = ""  # Буфер для флага с предыдущей строки

        for line in lines:
            line = line.strip()
            if not line: continue

            price_data = self._extract_price(line)

            if price_data:
                # Это строка с товаром
                price, name_part, comment_part = price_data
                
                # Определяем флаг
                flag = self._resolve_flag(name_part, comment_part, pending_flag)
                
                # Очищаем части от флагов и мусора
                name_clean = self._clean_text(name_part)
                comment_clean = self._clean_text(comment_part).lstrip('*)').strip()

                products.append(Product(
                    name=name_clean,
                    price=price,
                    flag=flag,
                    comment=comment_clean
                ))
                
                # Сбрасываем буфер, так как использовали флаг
                pending_flag = "" 
            else:
                # Это строка без цены (возможно, просто флаг)
                found_flag = TextExtractor.convert_emoji_to_latin(line)
                if found_flag and len(line) < 10:
                    pending_flag = found_flag

        return products

    def _extract_price(self, line: str) -> Optional[tuple]:
        """Ищет цену и делит строку. Возвращает (price, name, comment) или None."""
        clean_line = line.replace('*', '')
        # Регулярка для цены > 500, исключая даты и 4/128
        matches = list(re.finditer(r'(?<!/)\b(\d{1,3}(?:[., ]\d{3})*|\d{4,})\b', clean_line))
        
        if not matches:
            return None

        # Берем последнее валидное число
        for m in reversed(matches):
            val_str = re.sub(r'[^\d]', '', m.group(1))
            val = int(val_str)
            
            if 500 < val < 2000000:
                price_str = m.group(1)
                # Делим строку
                price_idx = line.rfind(price_str)
                if price_idx != -1:
                    name = line[:price_idx].strip()
                    comment = line[price_idx + len(price_str):].strip()
                    return val, name, comment
        return None

    def _resolve_flag(self, name: str, comment: str, pending: str) -> str:
        """Определяет флаг из буфера или текста."""
        if pending:
            return pending
            
        # Ищем в имени
        flag = TextExtractor.convert_emoji_to_latin(name)
        if flag: return flag
        
        # Ищем в комментарии
        flag = TextExtractor.convert_emoji_to_latin(comment)
        if flag: return flag
        
        return ""

    def _clean_text(self, text: str) -> str:
        """Удаляет эмодзи флагов и лишние символы."""
        # Удаляем Unicode-флаги
        text = re.sub(r'[\U0001F1E6-\U0001F1FF]{2}', '', text)
        # Удаляем дефисы на концах
        if text.strip().endswith('-'):
            return text.strip()[:-1].strip()
        return text.strip()

# --- 5. Точка входа (Application Layer) ---
class App:
    def __init__(self, url: str):
        self.url = url
        self.client = TelegramClient()
        self.extractor = TextExtractor()
        self.parser = PriceParser()

    def run(self):
        print(f"Запуск парсера для {self.url}...")
        
        html = self.client.fetch_html(self.url)
        if not html:
            return

        text = self.extractor.html_to_text(html)
        if not text:
            print("Не удалось извлечь текст.")
            return

        products = self.parser.parse(text)
        
        if products:
            self.print_results(products)
        else:
            print("Товары не найдены.")

    def print_results(self, products: List[Product]):
        print("-" * 90)
        print(f"{'ФЛАГ':<5} | {'ТОВАР':<40} | {'ЦЕНА':<8} | {'КОММЕНТ'}")
        print("-" * 90)
        for p in products:
            print(p)

if __name__ == '__main__':
    LINK = 'https://t.me/BigSaleApple/11198?embed=1'
    app = App(LINK)
    app.run()