import urllib3
import requests
import argparse
import os
import logging
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
    url = response.url
    response = get_response(url)
    check_for_redirect(response)
    return response
   

def print_directory(folder):
    file_directory = os.path.realpath(os.curdir)
    print(file_directory)
    try:
        print(os.path.join('{}', '{}').format(file_directory, folder))
    except:
        None


def download_txt(response, book_page_information):
    folder = args.folder_books
    if args.find_out_directory == 'yes':
        print_directory(folder)

    catalog_books = os.path.join('{}', '{}.txt').format(
    sanitize_filename(folder), sanitize_filename(book_page_information['filename']))
    os.makedirs(folder, exist_ok=True)
    
    with open(catalog_books, 'w', encoding='utf-8') as file:
        file.write(response.text)
        

def download_image(book_page_information):
    folder = args.folder_img
    if args.find_out_directory == 'yes':
        print_directory(folder)

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
    parser.add_argument('start_id', help='от какой странице', type=int)
    parser.add_argument('end_id', help='до какой странице', type=int)
    parser.add_argument('--skip_txt', help='не скачивать книги', type=int)
    parser.add_argument('--skip_imgs', help='не скачивать обложку', type=int)
    parser.add_argument('--folder_books', default='books', help='указать название папки для  загрузки книги')
    parser.add_argument('--folder_img', default='img', help='указать название папки для  загрузки обложки')
    parser.add_argument('--find_out_directory', help='show the directory? - yes')
    args = parser.parse_args()
    return args


def get_book_card_numbers(number):
    url = 'https://tululu.org/l55/{}'.format(number)
    response = get_response(url)
    soup = BeautifulSoup(response.text, "html.parser")
    book_card_numbers = soup.select('table.d_book')   
    return book_card_numbers


def parse_book(books_urls, books_id):
    for url, book_id in zip(books_urls[0], books_id):
        response = get_response(url)
        soup = BeautifulSoup(response.text, "html.parser")
        filename = soup.select_one('table.tabs td.ow_px_td h1').text
        image_name = soup.select_one('table.tabs td.ow_px_td table img')['src']
        genre = soup.select_one('table.tabs span.d_book a').text
        book_page_information = {
            'filename': filename.split('::')[0],
            'author': filename.split('::')[1],
            'image_name': image_name,
            'genres': [
            genre
            ]
        }
        response = get_book_link(book_id)
        meeting_the_specified_conditions(response, book_page_information)


def meeting_the_specified_conditions(response, book_page_information):
    if args.skip_txt == None:
        download_txt(response, book_page_information)

    if args.skip_imgs == None:
        download_image(book_page_information)


def get_books_urls(book_card_numbers):
    urls = []
    books_id = []
    
    for book_card_number in book_card_numbers:
        book_id = book_card_number.select_one('a')['href']
        url = urljoin('https://tululu.org', book_id)
        urls.append(url)
        books_id.append(book_id)
    return urls, books_id


if __name__ == '__main__':
    args = get_args()
    logging.basicConfig(level = logging.ERROR)
    urllib3.disable_warnings()
    books_urls = []
    books_id = []

    for number in range(args.start_id, args.end_id):
        book_card_numbers = get_book_card_numbers(number)
        urls, books_id = get_books_urls(book_card_numbers)
        books_urls.append(urls)
        books_id.append(books_id)
    try:    
        parse_book(books_urls, books_id)

    except requests.HTTPError:
        logging.error('Такого id нет на сайте')
