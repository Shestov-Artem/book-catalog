# Поиск книг по названию

import psycopg2
from tabulate import tabulate
from rich.console import Console

# Инициализация rich
console = Console()

def search_books_with_pagination(search_query: str, page_size: int = 5):
    """
    Поиск книг с постраничным выводом
    """
    conn = None
    current_page = 0
    total_pages = 0
    
    try:
        conn = psycopg2.connect(
            dbname="library",
            user="postgres",
            password="123",
            host="localhost",
            port="5432"
        )
        
        while True:
            with conn.cursor() as cursor:
                # Запрос для получения данных
                data_query = """
                    SELECT 
                        b.title AS "Название книги",
                        COALESCE(STRING_AGG(a.name, ', '), 'Не указан') AS "Авторы",
                        COALESCE(b.publication_year::text, 'Не указан') AS "Год",
                        COALESCE(LEFT(b.description, 50) || '...', 'Нет описания') AS "Описание"
                    FROM books b
                    LEFT JOIN book_authors ba ON b.id = ba.book_id
                    LEFT JOIN authors a ON ba.author_id = a.id
                    WHERE b.title ILIKE %s
                    GROUP BY b.id
                    ORDER BY 
                        CASE WHEN b.publication_year IS NULL THEN 0
                        ELSE b.publication_year END DESC
                    LIMIT %s OFFSET %s
                """
                
                offset = current_page * page_size
                cursor.execute(data_query, (f"%{search_query}%", page_size, offset))
                results = cursor.fetchall()
                
                # Запрос для подсчета общего количества
                count_query = """
                    SELECT COUNT(DISTINCT b.id) 
                    FROM books b 
                    WHERE b.title ILIKE %s
                """
                cursor.execute(count_query, (f"%{search_query}%",))
                total_books = cursor.fetchone()[0]
                total_pages = (total_books + page_size - 1) // page_size
                
                if not results:
                    print("\nНичего не найдено.")
                    break
                
                # Вывод результатов
                print(f"\nРезультаты поиска по запросу '{search_query}':")
                print(f"Страница {current_page + 1} из {total_pages}")
                print(tabulate(
                    results,
                    headers=["Название", "Авторы", "Год", "Описание"],
                    tablefmt="fancy_grid",
                    maxcolwidths=[30, 25, 10, 40]
                ))
                print(f"\nНайдено книг: {total_books}")
                
                # Меню навигации
                print("\nДействия:")
                console.print("[yellow][N][/] Следующая страница" if current_page < total_pages - 1 else "")
                console.print("[yellow][P][/] Предыдущая страница" if current_page > 0 else "")
                console.print("[yellow][Q][/] Выход")
                
                choice = input("\nВаш выбор: ").upper()
                
                if choice == 'N' and current_page < total_pages - 1:
                    current_page += 1
                elif choice == 'P' and current_page > 0:
                    current_page -= 1
                elif choice == 'Q':
                    break
                else:
                    console.print("\n[red]Некорректный ввод. Попробуйте еще раз.[/]")
                
    except psycopg2.Error as e:
        print(f"\nОшибка при поиске: {e}")
    finally:
        if conn:
            conn.close()

def search_books():
    while True:
        search_query = input("Введите название книги, которую хотите найти: ")
        if not search_query or search_query == '':
            print("Название книги не может быть пустым, повторите попытку\n")
        else:
            break
    search_books_with_pagination(search_query)