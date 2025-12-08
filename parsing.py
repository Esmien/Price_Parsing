import re
from bs4 import BeautifulSoup
from typing import List, Optional, Tuple
from models import Product

class TextExtractor:
    """Отвечает за очистку HTML и превращение его в текст"""
    
    @staticmethod
    def html_to_text(html: str) -> Optional[str]:
        soup = BeautifulSoup(html, 'lxml')
        div = soup.find('div', class_='tgme_widget_message_text')
        
        if not div:
            return None
            
        # Заменяем <br> на переносы строк
        for br in div.find_all('br'):
            br.replace_with('\n')
            
        return div.get_text(separator='\n', strip=True)

    @staticmethod
    def convert_emoji_to_latin(text: str) -> str:
        """Ищет флаг-эмодзи и возвращает его (или код страны)"""
        # Ищем Unicode-флаги (например 🇦🇪)
        match = re.search(r'[\U0001F1E6-\U0001F1FF]{2}', text)
        if match:
            flag_char = match.group(0)
            # В данном случае возвращаем сам эмодзи, так красивее в таблице.
            # Если нужны буквы (AE), раскомментируй строку ниже:
            # return "".join([chr(ord(c) - 127397) for c in flag_char])
            return flag_char
        return ""

class PriceParser:
    """Бизнес-логика: превращает текст в список товаров"""
    
    def parse(self, raw_text: str) -> List[Product]:
        lines = raw_text.split('\n')
        products = []
        pending_flag = "" # Буфер для флага с предыдущей строки

        for line in lines:
            line = line.strip()
            if not line: continue

            price_data = self._extract_price(line)

            if price_data:
                # Нашли строку с ценой -> это товар
                price, name_part, comment_part = price_data
                
                # Определяем флаг (из буфера или из строки)
                flag = self._resolve_flag(name_part, comment_part, pending_flag)
                
                # Чистим текст
                name_clean = self._clean_text(name_part)
                comment_clean = self._clean_text(comment_part).lstrip('*)').strip()

                products.append(Product(
                    name=name_clean,
                    price=price,
                    flag=flag,
                    comment=comment_clean
                ))
                
                # Сбрасываем буфер
                pending_flag = "" 
            else:
                # Строка без цены -> возможно, это одинокий флаг
                found_flag = TextExtractor.convert_emoji_to_latin(line)
                # Если строка короткая и это флаг -> запоминаем
                if found_flag and len(line) < 10:
                    pending_flag = found_flag

        return products

    def _extract_price(self, line: str) -> Optional[Tuple[int, str, str]]:
        """Возвращает (цена, имя, коммент) или None"""
        clean_line = line.replace('*', '')
        # Ищем цены > 500, исключаем 4/128
        matches = list(re.finditer(r'(?<!/)\b(\d{1,3}(?:[., ]\d{3})*|\d{4,})\b', clean_line))
        
        if not matches: return None

        # Берем последнее валидное число
        for m in reversed(matches):
            val_str = re.sub(r'[^\d]', '', m.group(1))
            val = int(val_str)
            
            if 500 < val < 2000000:
                price_str = m.group(1)
                # Делим строку по цене (ищем с конца)
                price_idx = line.rfind(price_str)
                if price_idx != -1:
                    return val, line[:price_idx].strip(), line[price_idx + len(price_str):].strip()
        return None

    def _resolve_flag(self, name: str, comment: str, pending: str) -> str:
        if pending: return pending
        
        f = TextExtractor.convert_emoji_to_latin(name)
        if f: return f
        
        f = TextExtractor.convert_emoji_to_latin(comment)
        if f: return f
        
        return ""

    def _clean_text(self, text: str) -> str:
        # Удаляем флаги из текста, чтобы не дублировались
        text = re.sub(r'[\U0001F1E6-\U0001F1FF]{2}', '', text)
        if text.strip().endswith('-'):
            return text.strip()[:-1].strip()
        return text.strip()