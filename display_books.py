# Постраничный вывод всех книг c сортировками

import psycopg2
from tabulate import tabulate
from rich.console import Console

# Инициализация rich
console = Console()

def sort_show_books_paginated():
    try:

        # Запрашиваем количество книг у пользователя
        while True:
            try:
                print("Выберите сортировку:\n"
                "0 - Сортировка по алфавиту\n"
                "1 - Сортировка по году выпуска\n")
                comand = int(input("Введите номер выбранной сортировки: "))

                if comand < 0 or comand > 1:
                    console.print("[yellow]Некоректный ввод, будет выбрана сортировка по алфавиту[/]")
                    comand = 0
                    break
                elif comand == 1:
                    while True:
                        print("Уточните параметры сортировки:\n"
                        "1 - Сначала новые\n"
                        "2 - Сначала старые\n")
                        comand_2 = int(input("Введите номер выбранной сортировки: "))
                        if comand_2 < 1 or comand_2 > 2:
                            console.print("[yellow]Некоректный ввод, сначала будут отображены более новые книги[/]")
                            comand = 1
                            break
                        elif comand_2 == 1:
                            comand = 1
                            break
                        else:
                            comand = 2
                            break
                    break
                else:
                    break
            except ValueError:
                console.print("\n\n[red]Некорректный ввод. Повторите попытку[/]")

        # Подключение к БД
        conn = psycopg2.connect(
            dbname="book_catalog",
            user="postgres",
            password="123",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        # Получаем общее количество книг
        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]

        if total_books == 0:
            console.print("\n[yellow]В базе данных нет книг.[/]")
            return

        # Настройки пагинации
        page_size = 5  # Книг на странице
        current_page = 1
        total_pages = (total_books + page_size - 1) // page_size

        while True:
            # Вычисляем смещение
            offset = (current_page - 1) * page_size

            sql_query = """
            SELECT 
                b.title AS "Название книги",
                COALESCE(STRING_AGG(a.name, ', '), 'Не указан') AS "Автор(ы)",
                COALESCE(b.publication_year::text, 'Не указан') AS "Год выпуска",
                COALESCE(b.description, 'Нет описания') AS "Описание"
            FROM 
                books b
            LEFT JOIN 
                book_authors ba ON b.id = ba.book_id
            LEFT JOIN 
                authors a ON ba.author_id = a.id
            GROUP BY 
                b.id
            """

            # Сортировка по алфавиту
            if comand == 0:
                sql_query += """
                ORDER BY 
                    b.title
                LIMIT %s OFFSET %s
                """
            # Сортировка по годам (сначала новые)
            elif comand == 1:
                sql_query += """
                ORDER BY 
                    CASE 
                        WHEN b.publication_year IS NULL THEN 0  -- книги без года в конце
                        ELSE b.publication_year 
                    END DESC  -- сортировка по УБЫВАНИЮ года (новые → старые)
                LIMIT %s OFFSET %s
                """
            # Сортировка по годам (сначала старые)
            else:
                sql_query += """
                ORDER BY 
                    CASE 
                        WHEN b.publication_year IS NULL THEN 9999  -- книги без года в конце
                        ELSE b.publication_year 
                    END ASC  -- сортировка по возрастанию года
                LIMIT %s OFFSET %s
                """
            
            # Выполняем запрос
            cursor.execute(sql_query, (page_size, offset))
            books = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            
            # Выводим результат
            print(f"\nСтраница {current_page} из {total_pages}")
            print(tabulate(books, headers=column_names, tablefmt="fancy_grid", maxcolwidths=30))
            print(f"\nКниги {offset + 1}-{min(offset + page_size, total_books)} из {total_books}")

            # Меню навигации
            print("\nНавигация:")
            if current_page > 1:
                console.print("[yellow](P)[/] Предыдущая страница", end=" | ")
            if current_page < total_pages:
                console.print("[yellow](N)[/] Следующая страница", end=" | ")
            console.print("[yellow](Q)[/] Выход")

            # Обработка ввода пользователя
            while True:
                choice = input("Ваш выбор: ").upper()
                if choice == 'P' and current_page > 1:
                    current_page -= 1
                    break
                elif choice == 'N' and current_page < total_pages:
                    current_page += 1
                    break
                elif choice == 'Q':
                    return
                else:
                    console.print("\n[red]Некорректный ввод. Попробуйте еще раз.[/]")

    except psycopg2.Error as e:
        console.print(f"\n[red]Ошибка при работе с PostgreSQL: {e}[/]")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()