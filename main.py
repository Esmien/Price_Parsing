# класс нужен просто для удобства обращения, написан криво и архитектурно неправильно

import requests
from bs4 import BeautifulSoup
import re

class Parser:
    def __init__(self, url):
        self.url = url

    @staticmethod
    def parse_line(line: str) -> dict:
        """Разбирает строчку на части"""
        if len(line) < 5:
            return {'product': '', 'price': '', 'flag': ''}
        
        line = line.strip()

        price_match = re.search(r'-?\d{1,}\.?\d*/?\d*\*?$', line)
        if price_match:
            price = price_match.group(0)
            line = line[:price_match.start()].strip()
        else:
            price = ''
        
        product = line.strip()
        
        return {
            'product': product,
            'price': price.replace('*', ''),
            'flag': '',  # Флаг будет добавлен отдельно
        }


    def get_page(self) -> str | None:
        """Вытаскивает HTML-код страницы"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        try:
            response = requests.get(self.url, headers=headers)

            if response.status_code == 200:
                return response.text
            else:
                print(f'Ошибка: {response.status_code}')
                return None

        except requests.exceptions.RequestException as e:
            print(e)
            return None
        
    @staticmethod
    def extract_text(html: str) -> str | None:
        """Вытаскивает текст из нужной части страницы"""
        soup = BeautifulSoup(html, 'lxml')

        message = soup.find('div', class_='tgme_widget_message_text')
        if message:
            return message.get_text(separator='\n', strip=True)
        return None

def handle_dict(raw_dict: dict) -> dict:
    """Обрабатывает сырой словарь для вывода цены в нормальном виде"""
    clear_dict = {}

    for key, value in raw_dict.items():
        if key == 'price' and value:
            price_digits = ''.join(char for char in value if char.isdigit())
            clear_dict[key] = int(price_digits) if price_digits else 0
        else:
            clear_dict[key] = value

    return clear_dict

def main():
    """Точка входа в программу"""
    url = 'https://t.me/BigSaleApple/11198?embed=1'
    parser = Parser(url)

    print('Получаем HTML')
    html = parser.get_page()

    if html:
        print('HTML получен')
        print('Извлекаем текст')
        text = parser.extract_text(html).split('\n')

        if text:
            print('Текст извлечен')

            for line in text:
                parsed_line = parser.parse_line(line)
                if parsed_line:
                    res = handle_dict(parsed_line)

                    for key, value in res.items():
                        result = f'{key}: {value}' if value else ''
                        print(result, end='\t')
                    print()
        else:
            print('Текст не найден')
    else:
        print('HTML не получен')

if __name__ == '__main__':
    main()