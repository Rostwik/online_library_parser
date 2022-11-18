import os

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse, urlsplit


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

    filepath = os.path.join(folder, f'Комментарии к книге {filename}.txt')

    with open(filepath, 'w') as file:
        file.write(comments)


def check_for_redirect(response):
    if response.history:
        if response.url == 'https://tululu.org/':
            raise requests.HTTPError(response.url)


def main():
    site_url = 'https://tululu.org/'

    for id in range(10):
        try:
            title_url = f'{site_url}b{id + 1}'
            print(title_url)
            response = requests.get(title_url)
            response.raise_for_status()
            check_for_redirect(response)

            soup = BeautifulSoup(response.text, 'lxml')
            book_tag = soup.find('h1').text
            img_tag = soup.find(class_='bookimage').find('img')['src']

            title, _ = book_tag.split('::')

            download_url = f'{site_url}txt.php?id={id + 1}'
            unique_title = f'{id + 1}. {title.strip()}'

            book_filepath = download_txt(download_url, unique_title)


            comment_tag = soup.find_all(class_='texts')
            if comment_tag:
                book_comments = '\n'.join([comment.find(class_='black').text for comment in comment_tag])
                download_comments(book_comments, unique_title)


            #
            # filepath = download_image(urljoin(site_url, img_tag))
            # print(filepath)


        except requests.HTTPError as exp:
            print(exp)


if __name__ == '__main__':
    main()
