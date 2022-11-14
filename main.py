import requests
import os


def main():
    os.makedirs('books', exist_ok=True)

    for id in range(10):
        url = f'https://tululu.org/txt.php?id={id + 1}'
        print(url)

        response = requests.get(url)
        response.raise_for_status()

        filename = f'books/book{id}.txt'
        with open(filename, 'wb') as file:
            file.write(response.content)


if __name__ == '__main__':
    main()
