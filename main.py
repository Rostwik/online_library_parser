import os

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def download_txt(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    filepath = os.path.join(folder, f'{sanitize_filename(filename)}.txt')

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


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
            title, _ = book_tag.split('::')

            download_url = f'{site_url}txt.php?id={id + 1}'
            unique_title = f'{id + 1}. {title.strip()}'

            filepath = download_txt(download_url, unique_title)
            print(filepath)

        except requests.HTTPError as exp:
            print(exp)

    # print(soup.find('img', class_='attachment-post-image')['src'])
    # title_tag_post = soup.find('div', class_='entry-content')
    # print(title_tag_post.text)


if __name__ == '__main__':
    main()
