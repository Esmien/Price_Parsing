import requests
from bs4 import BeautifulSoup
import re

def parse_line(line):
    if len(line) < 5:
        return {'product': '', 'price': '', 'flag': ''}

    price_match = re.search(r'-?\d{1,}\.?\d*/?\d*\*?$', line)
    if price_match:
        price = price_match.group(0)
        # Удаляем цену из строки
        line = line[:price_match.start()].strip()
    else:
        price = ''

    flag_match = re.search(r'[🇦-🇿]{2}', line)

    if flag_match:
        flag = flag_match.group(0)
        # Удаляем флаг из строки
        line = line.replace(flag, '').strip()
    else:
        flag = ''
    product = line.strip()
    return {
        'product': product,
        'price': price.replace('*', ''),
        'flag': flag,
    }

def get_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print(f'Ошибка: {response.status_code}')
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None

def extract_text(html):
    soup = BeautifulSoup(html, 'lxml')

    message = soup.find('div', class_='tgme_widget_message_text')
    if message:
        return message.get_text(separator='\n', strip=True)
    return None

def handle_dict(raw_dict):
    #ToDo заебашить нормальную обработку
    clear_dict = {}
    for key, value in raw_dict.items():
        if key == 'price' and value:  # Проверяем что цена не пустая
            # Убираем все кроме цифр
            price_digits = ''.join(char for char in value if char.isdigit())

            # Преобразуем в int (если есть цифры)
            clear_dict[key] = int(price_digits) if price_digits else 0
        else:
            clear_dict[key] = value

    return clear_dict

def main():
    url = 'https://t.me/BigSaleApple/11198?embed=1'
    print('Получаем HTML')
    html = get_page(url)
    if html:
        print('HTML получен')
        print('Извлекаем текст')
        text = extract_text(html).split('\n')
        if text:
            print('Текст извлечен')
            for line in text:
                parsed_line = parse_line(line)
                if parsed_line:
                    res = handle_dict(parsed_line)
                    for key, value in res.items():
                        result = f'{key}: {value}' if value else ''
                        print(result, end='\t')
                    print()
            print("=" * 50)
            # print(text)
            print("=" * 50)
        else:
            print('Текст не найден')
    else:
        print('HTML не получен')

if __name__ == '__main__':
    main()