import urllib3
import requests
import argparse
import os
import logging
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    history = response.history
  
    if history:
        raise requests.HTTPError(history)  


def get_response(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    return response


def get_book_link(book_id):
    book_id = book_id.rsplit('b')[1]
    payload = {'id': '{}'.format(book_id)}
    response = requests.get('https://tululu.org/txt.php', params=payload, verify=False)
    response = get_response(response.url)
    check_for_redirect(response)
    return response


def download_txt(response, book_page_information):
    folder = args.folder_books
    if args.find_out_directory:
        logging.info(os.path.join('{}', '{}').format(os.path.realpath(os.curdir), folder))

    catalog_books = os.path.join('{}', '{}.txt').format(
    sanitize_filename(folder), sanitize_filename(book_page_information['filename']))
    os.makedirs(folder, exist_ok=True)
    
    with open(catalog_books, 'w', encoding='utf-8') as file:
        file.write(response.text)


def download_image(book_page_information):
    folder = args.folder_img
    if args.find_out_directory:
        logging.info(os.path.join('{}', '{}').format(os.path.realpath(os.curdir), folder))

    filename = book_page_information['image_name']
    url = 'https://tululu.org/{}'.format(filename)
    response = get_response(url)
    filename = filename.split("/")[2]
    catalog_img = os.path.join('{}', '{}').format(folder, filename)
    os.makedirs(folder, exist_ok=True)

    with open(catalog_img, 'wb') as file:
        file.write(response.content)


def get_args():
    parser = argparse.ArgumentParser(description='Получение ссылок на книги')
    parser.add_argument('start_page', default='1', help='от какой страницы', type=int)
    args, unknown = parser.parse_known_args()
    parser.add_argument('--end_page', default=args.start_page+1, help='до какой страницы', type=int)
    parser.add_argument('--skip_txt', default=False, action='store_true', help='не скачивать книги')
    parser.add_argument('--skip_imgs', default=False, action='store_true', help='не скачивать обложку')
    parser.add_argument('--folder_books', default='books', help='указать название папки для  загрузки книги')
    parser.add_argument('--folder_img', default='img', help='указать название папки для  загрузки обложки')
    parser.add_argument('--find_out_directory', default=False, action='store_true', help='show the directory?')
    parser.add_argument('--json_path', default=os.path.abspath(os.curdir), help='можно указать куда сохранить фаил json')
    args = parser.parse_args()
    return args


def get_book_ids(id):
    url = 'https://tululu.org/l55/{}'.format(id)
    response = get_response(url)
    soup = BeautifulSoup(response.text, "html.parser")
    book_card_numbers = soup.select('table.d_book')   
    return book_card_numbers


def parse_book(urls_and_books_ids):
    for url, book_id in zip(urls_and_books_ids['urls'], urls_and_books_ids['books_ids']):
        response = get_response(url)
        soup = BeautifulSoup(response.text, "html.parser")
        filename = soup.select_one('table.tabs td.ow_px_td h1').text
        image_name = soup.select_one('table.tabs td.ow_px_td table img')['src']
        genre = soup.select_one('table.tabs span.d_book a').text
        book_page_information = {
            'filename': filename.split('::')[0],
            'author': filename.split('::')[1],
            'image_name': image_name,
            'genres': [genre]
        }
        json_path = os.path.join(args.json_path, 'book_page_information.json')
        with open(json_path, "w") as my_file:
            json.dump(book_page_information,my_file)

        response = get_book_link(book_id)

        if not args.skip_txt:
            download_txt(response, book_page_information)

        if not args.skip_imgs:
            download_image(book_page_information)


def get_books_urls_and_ids(book_card_numbers):
    urls = []
    books_ids = []

    for book_card_number in book_card_numbers:
        book_id = book_card_number.select_one('a')['href']
        url = urljoin('https://tululu.org', book_id)
        urls.append(url)
        books_ids.append(book_id)
    return {
        'urls': urls,
        'books_ids': books_ids
    }


if __name__ == '__main__':
    args = get_args()
    logging.basicConfig(level = logging.INFO)
    urllib3.disable_warnings()

    for page_number in range(args.start_page, args.end_page):
        book_card_numbers = get_book_ids(page_number)
        urls_and_books_ids = get_books_urls_and_ids(book_card_numbers) 
    try:
        parse_book(urls_and_books_ids)

    except requests.HTTPError:
        logging.error('Такого страницы нет на сайте')
