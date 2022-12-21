import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlsplit
from main import check_for_redirect, download_txt, download_image, download_comments, parse_book_page
import json

url = 'https://tululu.org/l55/'

for page in range(2):

    page_url = urljoin(url, str(page + 1))
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

            print(book_download_attributes)

            books_json = json.dumps(book_download_attributes, ensure_ascii=False)

            with open("books.json", "a") as file:
                file.write(books_json)

        except requests.HTTPError as exp:
            print(exp)
        except requests.exceptions.ConnectionError:
            print('Интернет исчез')
            time.sleep(5)
