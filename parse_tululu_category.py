import urllib3
import requests
import argparse
import os
import codecs
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


def parse_first_book(number):
    book_page_information = {}
    url = 'https://tululu.org/l55/{}'.format(number)
    response = get_response(url)
    soup = BeautifulSoup(response.text, "html.parser")
    book_card_numbers = soup.find_all('table', class_='d_book')
    for book_card_number in book_card_numbers:
        book_id = book_card_number.find('a')['href']
        url = urljoin('https://tululu.org', book_id)
        response = get_response(url)
        soup = BeautifulSoup(response.text, "html.parser")        
        filename = soup.find('table', class_='tabs').find('td', class_='ow_px_td').find('h1').text
        image_name = soup.find('table', class_='tabs').find('td', class_='ow_px_td').find('table').find('img')['src']
        genre = soup.find('table', class_='tabs').find('span', class_='d_book').find('a').text
        book_page_information = {
            'filename': filename.split('::')[0],
            'author': filename.split('::')[1],
            'image_name': image_name,
            'genres': [
            genre
            ]
        }
        response = get_book_link(book_id) 
        download_txt(response, book_page_information)
        download_image(book_page_information)


def get_book_link(book_id):
    book_id = book_id.rsplit('b')[1]
    payload = {'id': '{}'.format(book_id)}
    response = requests.get('https://tululu.org/txt.php', params=payload, verify=False)
    url = response.url
    response = get_response(url)
    check_for_redirect(response)
    return response
    

def download_txt(response, book_page_information, folder='books'):
    catalog_books = os.path.join('{}', '{}.txt').format(
    sanitize_filename(folder), sanitize_filename(book_page_information['filename']))
    os.makedirs(folder, exist_ok=True)
    
    with open(catalog_books, 'w', encoding='utf-8') as file:
        file.write(response.text)
        

def download_image(book_page_information, folder = 'img'):
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
    args = parser.parse_args()
    return args
    

if __name__ == '__main__':
    args = get_args()
    for number in range(args.start_id, args.end_id):
        parse_first_book(number)
