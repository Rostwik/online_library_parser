import time

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlsplit
from main import check_for_redirect, download_txt, download_image, download_comments, parse_book_page
import json
import argparse

url = 'https://tululu.org/l55/'

parser = argparse.ArgumentParser(description='''Программа скачивает книги в формате txt,'
                                                 а также обложки и комментарии в отдельные папки.
                                                 Формирует json файл с данными скачиваемых книг и сохраняет его
                                                 в указанной директории.
                                                 Для работы программы в командной строке необходимо ввести
                                                 два обязательных параметра: номер страницы начала и номер страницы
                                                 окончания интервала скачиваемых книг.                                                 
                                                 ''')
parser.add_argument('--start_page', help='Начало интервала', type=int, default=1)
parser.add_argument('--end_page', help='Конец интервала', type=int, default=10)
args = parser.parse_args()

for page in range(args.start_page, args.end_page):

    page_url = urljoin(url, str(page))
    response = requests.get(page_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    book_tags = soup.select('.d_book .bookimage a')

    for book in book_tags:

        try:
            book_url = urljoin(page_url, book['href'])
            print(book_url)
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)

            soup = BeautifulSoup(response.text, 'lxml')
            book_download_attributes = parse_book_page(soup)

            unique_title = f"{book_download_attributes['title']}"
            txt_url = 'https://tululu.org/txt.php'
            book_number = urlsplit(book_url).path.replace('b', '').split('/')[1]

            book_download_attributes['book_path'] = download_txt(txt_url, book_number, unique_title)

            book_download_attributes['img_url'] = download_image(urljoin(book_url, book_download_attributes['img_url']))

            books_json = json.dumps(book_download_attributes, ensure_ascii=False)

            with open("books.json", "a") as file:
                file.write(books_json)

        except requests.HTTPError as exp:
            print(exp)
        except requests.exceptions.ConnectionError:
            print('Интернет исчез')
            time.sleep(5)
