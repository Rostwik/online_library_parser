import os

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse, urlsplit
import argparse


def parse_book_page(soup):
    book_info = dict()

    book_info['img_url'] = soup.find(class_='bookimage').find('img')['src']

    book_tag = soup.find('h1').text
    title, author = book_tag.split('::')
    book_info['title'] = title.strip()
    book_info['author'] = author.strip()

    comment_tag = soup.find_all(class_='texts')
    book_info['book_comments'] = []
    if comment_tag:
        book_comments = '\n'.join([comment.find(class_='black').text for comment in comment_tag])
        book_info['book_comments'] = book_comments

    genre_tag = soup.find('span', class_='d_book')

    book_info['genres'] = []
    if genre_tag:
        genre_list = [genre.text for genre in genre_tag.find_all('a')]
        book_info['genres'] = genre_list

    return book_info


def download_txt(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    filepath = os.path.join(folder, f'{sanitize_filename(filename)}.txt')

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def download_image(url, folder='images/'):
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
        if response.url == 'https://tululu.org/':
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

    for id in range(args.start_id, args.end_id + 1):
        try:
            book_url = f'{site_url}b{id}'

            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)

            soup = BeautifulSoup(response.text, 'lxml')
            book_info = parse_book_page(soup)

            unique_title = f"{id}. {book_info['title']}"
            txt_url = f'{site_url}txt.php?id={id}'
            download_txt(txt_url, unique_title)

            download_image(urljoin(site_url, book_info['img_url']))
            if book_info['book_comments']:
                download_comments(book_info['book_comments'], unique_title)

            print(f"Название: {book_info['title']}")
            print(f"Автор: {book_info['author']}")
            print(f"Жанр: {book_info['genres']}\n")

        except requests.HTTPError as exp:
            print(exp)


if __name__ == '__main__':
    main()
