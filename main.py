import os

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse, urlsplit


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
    print(filepath)
    print(comments)

    with open(filepath, 'w') as file:
        file.write(comments)


def check_for_redirect(response):
    if response.history:
        if response.url == 'https://tululu.org/':
            raise requests.HTTPError(f'Книги нет, редирект на {response.url}')


def main():
    site_url = 'https://tululu.org/'

    for id in range(10):
        try:
            title_url = f'{site_url}b{id + 1}'

            response = requests.get(title_url)
            response.raise_for_status()
            check_for_redirect(response)

            soup = BeautifulSoup(response.text, 'lxml')
            book_info = parse_book_page(soup)

            unique_title = f"{id + 1}. {book_info['title']}"
            download_url = f'{site_url}txt.php?id={id + 1}'
            download_txt(download_url, unique_title)

            download_image(urljoin(site_url, book_info['img_url']))

            if book_info['book_comments']:
                download_comments(book_info['book_comments'], unique_title)

        except requests.HTTPError as exp:
            print(exp)


if __name__ == '__main__':
    main()
