# Working with online parsing.

The project was created for downloading books and images.

## How to start

[Python3](https://www.python.org/downloads/) should be already installed.

Use pip to install dependencies:

```bash
pip install -r requirements.txt
```

### Run

example:

```
$ python parsing.py 1 10
```

### You will see

Titles\author\comments of books and so on.
```
Блеск и нищета информационных технологий. Почему ИТ не являются конкурентным преимуществом  
   Карр Николас Дж
Интересная книженция: полезная, легко читается, не много воды.
Деловая литература
```

### Optional parameters argparse

--skip_txt  = не скачивать книги
--skip_imgs = не скачивать книги
--folder_books = указать название папки для  загрузки книги.  default='books'
--folder_img = указать название папки для  загрузки обложки.  default='img'

example:

```
$ python parsing.py 1 10 --skip_txt 1 --skip_imgs 1 --folder_books books --folder_imgs
```

# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org).
