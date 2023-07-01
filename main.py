import os
import time

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse, urlsplit
import argparse


def parse_book_page(soup):
    book_tag = soup.find('h1').text
    title, author = book_tag.split('::')
    comment_tag = soup.select('.texts .black')
    genre_tag = soup.select('span.d_book a')

    book_download_attributes = {
        'title': title.strip(),
        'author': author.strip(),
        'img_url': soup.select_one('.bookimage img')['src'],
        'book_comments': '\n'.join([comment.text for comment in comment_tag]),
        'genres': [genre.text for genre in genre_tag]
    }

    return book_download_attributes


def download_txt(url, id, filename, path):
    folder = os.path.join(path, 'books/')
    os.makedirs(folder, exist_ok=True)

    payload = {
        'id': id
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)

    filepath = os.path.join(folder, f'книга {id} {sanitize_filename(filename)}.txt')

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def download_image(url, path):
    folder = os.path.join(path, 'images/')
    os.makedirs(folder, exist_ok=True)

    filename = urlsplit(url).path.split('/')[-1]

    response = requests.get(url)
    response.raise_for_status()

    filepath = os.path.join(folder, filename)

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def download_comments(comments, filename, folder='comments/'):
    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, f'Комментарии к книге {sanitize_filename(filename)}.txt')

    with open(filepath, 'w') as file:
        file.write(comments)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError(f'Книги нет, редирект на {response.url}')


def main():
    parser = argparse.ArgumentParser(description='''Программа скачивает книги в формате txt,'
                                                 а также обложки и комментарии в отдельные папки.
                                                 Для работы программы в командной строке необходимо ввести
                                                 два обязательных параметра: id начала и id окончания интервала
                                                 скачиваемых книг.
                                                 ''')
    parser.add_argument('--start_id', help='Начало интервала', type=int, default=1)
    parser.add_argument('--end_id', help='Конец интервала', type=int, default=10)
    args = parser.parse_args()

    site_url = 'https://tululu.org/'

    for book_number in range(args.start_id, args.end_id + 1):
        try:
            book_url = f'{site_url}b{book_number}/'

            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)

            soup = BeautifulSoup(response.text, 'lxml')
            book_download_attributes = parse_book_page(soup)

            unique_title = f"{book_number}. {book_download_attributes['title']}"
            txt_url = f'{site_url}txt.php'
            download_txt(txt_url, book_number, unique_title)

            download_image(urljoin(book_url, book_download_attributes['img_url']))
            if book_download_attributes['book_comments']:
                download_comments(book_download_attributes['book_comments'], unique_title)

            print(f"Название: {book_download_attributes['title']}")
            print(f"Автор: {book_download_attributes['author']}")
            print(f"Жанр: {book_download_attributes['genres']}\n")

        except requests.HTTPError as exp:
            print(exp)
        except requests.exceptions.ConnectionError:
            print('Интернет исчез')
            time.sleep(5)


if __name__ == '__main__':
    main()
