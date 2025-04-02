# Создаем базу данных и таблицы к ней

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    # Подключаемся к стандартной базе данных postgres для создания новой БД
    conn = psycopg2.connect(
        dbname="postgres",  # Подключаемся к стандартной БД
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # Необходимо для создания БД
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("CREATE DATABASE book_catalog")  # Пытаемся создать БД
        print("База данных 'book_catalog' успешно создана!")
    except psycopg2.Error as e:
        print(f"База данных уже существует или произошла ошибка: {e}")
    finally:
        cursor.close()
        conn.close()

def create_tables():
    # Подключение к БД
    conn = psycopg2.connect(
        dbname="book_catalog",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )

    cursor = conn.cursor()

    # Создание таблиц (SQL из предыдущего примера)
    create_tables_sql = """
    -- Таблица книг
    CREATE TABLE IF NOT EXISTS books (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        publication_year INTEGER,
        description TEXT
    );

    -- Таблица авторов
    CREATE TABLE IF NOT EXISTS authors (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL
    );

    -- Связь книги и авторов (многие-ко-многим)
    CREATE TABLE IF NOT EXISTS book_authors (
        book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
        author_id INTEGER REFERENCES authors(id) ON DELETE CASCADE,
        PRIMARY KEY (book_id, author_id)
    );
    """

    cursor.execute(create_tables_sql)
    conn.commit()  # Сохраняем изменения

    print("Таблицы успешно созданы!")

    # Закрываем соединение
    cursor.close()
    conn.close()