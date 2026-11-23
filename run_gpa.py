"""Khởi chạy Student GPA Lab từ PowerShell."""

import argparse
from contextlib import closing
from pathlib import Path
import sqlite3
import sys

from gpa_lab import open_db
from gpa_menu import run_menu

ROOT = Path(__file__).resolve().parent


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Tính điểm môn và GPA học kỳ")
    parser.add_argument("--sample", action="store_true", help="Mở dữ liệu giả lập")
    args = parser.parse_args()
    filename = "sample.db" if args.sample else "student.db"
    try:
        with closing(open_db(ROOT / "database" / filename, sample=args.sample)) as db:
            print("Student GPA Lab — " + ("Dữ liệu giả lập" if args.sample else "Dữ liệu cá nhân"))
            run_menu(db)
    except (OSError, sqlite3.Error) as error:
        parser.exit(1, f"Không mở được dữ liệu: {error}\n")


if __name__ == "__main__":
    main()

