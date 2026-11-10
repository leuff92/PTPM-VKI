import argparse
import sqlite3
from pathlib import Path

import requests

from src.database import DatabaseRepository
from src.parser import ForumParser


ROOT = Path(__file__).resolve().parent


def main(argv=None) -> int:
    arguments = argparse.ArgumentParser(description="Сбор сообщений учебного форума")
    arguments.add_argument("--url", help="Адрес страницы с разметкой учебного форума")
    arguments.add_argument("--db", default=str(ROOT / "comments.db"), help="Файл SQLite")
    args = arguments.parse_args(argv)

    try:
        parser = ForumParser()
        if args.url:
            comments = parser.parse_page(args.url)
        else:
            html = (ROOT / "data" / "forum.html").read_text(encoding="utf-8")
            comments = parser.parse_html(html)

        repository = DatabaseRepository(args.db)
        try:
            saved = parser.save_to_db(comments, repository)
            print(f"Найдено сообщений: {len(comments)}")
            print(f"Добавлено в базу: {saved}")
            for comment in comments:
                print(f"{comment['id']} | {comment['name']} | {comment['message']}")
            print(f"База данных: {args.db}")
        finally:
            repository.close()
    except (requests.RequestException, sqlite3.Error, OSError, TypeError, ValueError) as error:
        print(f"Ошибка: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
