import psycopg2

def add_book_manually():
    # Подключение к БД
    conn = psycopg2.connect(
        dbname="book_catalog",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    try:
        # Ввод данных о книге
        print("\nДобавление новой книги:")
        title = input("Название книги: ")
        if not title:
            print("Книга без названия не может быть добавлена")
            return
        year = input("Год публикации (оставьте пустым, если неизвестно): ")
        description = input("Описание (оставьте пустым, если нет): ")

        # Добавляем книгу
        cursor.execute(
            "INSERT INTO books (title, publication_year, description) VALUES (%s, %s, %s) RETURNING id",
            (title, int(year) if year else None, description if description else None)
        )
        book_id = cursor.fetchone()[0]

        # Множество для отслеживания уже добавленных авторов
        added_authors = set()

        # Добавляем авторов
        while True:
            author_name = input("Имя автора (оставьте пустым чтобы закончить): ").strip()
            if not author_name:
                break
            
            # Проверяем, есть ли автор в базе
            cursor.execute("SELECT id FROM authors WHERE name = %s", (author_name,))
            author = cursor.fetchone()
            
            if author:
                author_id = author[0]
                print(f"Автор {author_name} уже есть в базе (ID: {author_id})")
            else:
                cursor.execute(
                    "INSERT INTO authors (name) VALUES (%s) RETURNING id",
                    (author_name,)
                )
                author_id = cursor.fetchone()[0]
                print(f"Добавлен новый автор (ID: {author_id})")
            
            # Проверяем, не добавляли ли уже этого автора для этой книги
            if author_id not in added_authors:
                cursor.execute(
                    "INSERT INTO book_authors (book_id, author_id) VALUES (%s, %s)",
                    (book_id, author_id)
                )
                added_authors.add(author_id)
            else:
                print(f"Автор {author_name} уже привязан к этой книге, пропускаем...")

        conn.commit()
        print(f"\nКнига '{title}' успешно добавлена с ID: {book_id}")

    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
    finally:
        cursor.close()
        conn.close()