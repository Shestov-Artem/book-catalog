import psycopg2
import requests
from bs4 import BeautifulSoup

def parse_book_page(book_url):
    try:
        # Получаем содержимое страницы
        response = requests.get(book_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Извлекаем название книги
        title_tag = soup.find('h1', class_='max200')
        title = title_tag.text.strip() if title_tag else None

        authors = []  # Теперь это список
        author_spans = soup.find_all('span', class_=lambda x: x and 'author' in x.split())
        
        for span in author_spans:
            author_tag = span.find('a')
            if author_tag:
                author_name = author_tag.text.strip()
                # Проверяем, что автор еще не добавлен
                if author_name and author_name not in authors:
                    authors.append(author_name)

        # Извлекаем описание книги
        description_tag = soup.find('p', class_='book')
        description = description_tag.text.strip() if description_tag else None

        # Извлекаем год издания из таблицы с информацией о книге
        year = None
        info_table = soup.find('table', class_='table-borderless')
        if info_table:
            for row in info_table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2 and 'Год издания' in cells[0].text:
                    year_text = cells[1].text.strip()
                    if year_text.isdigit():
                        year = int(year_text)
                    break

        return {
            'title': title,
            'author': authors,
            'year': year,
            'description': description
        }

    except Exception as e:
        print(f"Ошибка при парсинге страницы {book_url}: {str(e)}")
        return None



def add_book_to_db(cursor, title, year=None, description=None, authors=[]):
    """Универсальная функция для добавления книги"""
    try:
        # Добавляем книгу
        cursor.execute(
            """INSERT INTO books (title, publication_year, description) 
            VALUES (%s, %s, %s) RETURNING id""",
            (title, year, description)
        )
        book_id = cursor.fetchone()[0]
        
        print("BD: ", authors)
        # Добавляем авторов
        for author_name in authors:
            print("in BD", author_name)
            # Проверяем существование автора
            cursor.execute("SELECT id FROM authors WHERE name = %s", (author_name,))
            author = cursor.fetchone()
            
            if author:
                author_id = author[0]
            else:
                cursor.execute(
                    "INSERT INTO authors (name) VALUES (%s) RETURNING id",
                    (author_name,)
                )
                author_id = cursor.fetchone()[0]
            
            # Создаем связь
            cursor.execute(
                "INSERT INTO book_authors (book_id, author_id) VALUES (%s, %s)",
                (book_id, author_id)
            )
        
        return book_id
    
    except Exception as e:
        raise e

# Пример использования
def parse_book():

    conn = psycopg2.connect(
        dbname="book_catalog",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    
    try:

        while True:
            book_url = input("Введите ссылку на книку: ")
            if book_url:
                break
            else:
                print("Ссылка не может быть пустой")

        book_data = parse_book_page(book_url)

        if book_data:
            try:
                title = book_data['title']
                authors = book_data['author']
                year = book_data['year']
                description = book_data['description']
            
                print("Авторы: ", authors)

                # Добавляем книгу
                new_book_id = add_book_to_db(cursor, title, year, description, authors)
                
                conn.commit()
                print(f"Книга добавлена с ID: {new_book_id}")

            except Exception as e:
                conn.rollback()
                print(f"Ошибка при добавлении в БД: {e}")
        else:
            print("Не удалось получить данные о книге")

    
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
    finally:
        cursor.close()
        conn.close()