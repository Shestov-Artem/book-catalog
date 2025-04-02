from init_db import create_tables, create_database
from add_book_manually import add_book_manually
from add_book_by_parse import parse_book
from book_search import search_books
from display_books import sort_show_books_paginated

from rich.console import Console
from rich.panel import Panel

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style as PromptStyle

# Инициализация rich
console = Console()

def help_menu():
    console.print(Panel.fit(
        "[bold]Доступные команды:[/]\n"
        "[yellow]help[/] - показать справку\n"
        "[yellow]init_database[/] - инициализировать БД\n"
        "[yellow]add_book[/] - добавить новую книгу вручную\n"
        "[yellow]parse_book[/] - добавить новую книгу парсингом\n"
        "[yellow]search_books[/] - найти книгу по названию\n"
        "[yellow]view_books[/] - показать все книги\n"
        "[yellow]exit[/] - выйти из программы",
        title="[bold]Справка[/]",
        border_style="white"
    ))

# Кастомизированное автодополнение с описанием
class CustomCompleter(WordCompleter):
    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for cmd in COMMANDS:
            if cmd.startswith(word.lower()):
                if cmd == "help":
                    yield Completion(cmd, start_position=-len(word), display_meta="Показать справку")
                elif cmd == "init_database":
                    yield Completion(cmd, start_position=-len(word), display_meta="инициализировать БД")
                elif cmd == "add_book":
                    yield Completion(cmd, start_position=-len(word), display_meta="добавить новую книгу вручную")
                elif cmd == "parse_book":
                    yield Completion(cmd, start_position=-len(word), display_meta="добавить новую книгу парсингом")
                elif cmd == "search_books":
                    yield Completion(cmd, start_position=-len(word), display_meta="Найти книгу по названию")
                elif cmd == "view_books":
                    yield Completion(cmd, start_position=-len(word), display_meta="Показать все книги")
                elif cmd == "exit":
                    yield Completion(cmd, start_position=-len(word), display_meta="Выйти из программы")

COMMANDS = ["help", "init_database", "add_book", "parse_book", "search_books", "view_books", "exit"]
completer = CustomCompleter(COMMANDS, ignore_case=True)

# Стиль для prompt_toolkit
prompt_style = PromptStyle.from_dict({
    "completion-menu.completion": "bg:#ba8e09 #000000",
    "completion-menu.completion.current": "bg:#ffffff #e8b10c",
    "scrollbar.button": "bg:#000000",
})

def main():
    console.print(Panel.fit(
        "Введите [yellow]help[/] для списка команд",
        title="[bold]Программа управления БД[/]",
        border_style="white"
    ))

    while True:
        try:
            command = prompt(
                "> ",
                completer=completer,
                history=FileHistory("cmd_history.txt"),
                style=prompt_style,
                complete_while_typing=True,
            ).strip().lower()

            if command == "help":
                help_menu()
            elif command == "init_database":
                create_database()
                create_tables()
            elif command == "add_book":
                add_book_manually()
            elif command == "parse_book":
                parse_book()
            elif command == "search_books":
                search_books()
            elif command == "view_books":
                sort_show_books_paginated()
            elif command == "exit":
                console.print("[yellow]Выход из программы...[/]")
                break
            else:
                console.print(f"[yellow]Ошибка:[/] Неизвестная команда [yellow]{command}[/]. Введите [yellow]help[/] для справки.")
        except KeyboardInterrupt:
            console.print("\n[yellow]Для выхода введите [red]exit[/].[/]")
        except EOFError:
            console.print("\n[yellow]Выход из программы.[/]")
            break

if __name__ == "__main__":
    main()