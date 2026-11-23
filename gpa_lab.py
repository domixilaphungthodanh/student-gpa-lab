from fractions import Fraction
from pathlib import Path
import re
import sqlite3

GRADE_FIELDS = ("process_1", "process_2", "midterm", "final")
WEIGHTS = (10, 20, 20, 50)
SCHEMA = """
CREATE TABLE IF NOT EXISTS semesters (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0)
) STRICT;

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY,
    semester_id INTEGER NOT NULL REFERENCES semesters(id),
    code TEXT NOT NULL COLLATE NOCASE CHECK(length(trim(code)) > 0),
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    credits INTEGER NOT NULL CHECK(credits > 0),
    process_1 INTEGER CHECK(process_1 BETWEEN 0 AND 1000),
    process_2 INTEGER CHECK(process_2 BETWEEN 0 AND 1000),
    midterm INTEGER CHECK(midterm BETWEEN 0 AND 1000),
    final INTEGER CHECK(final BETWEEN 0 AND 1000),
    UNIQUE(semester_id, code)
) STRICT;
"""


def open_db(path, sample=False):
    if str(path) != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA)
        if sample:
            seed_sample(connection)
    except BaseException:
        connection.close()
        raise
    return connection


def seed_sample(db):
    with db:
        semester = db.execute(
            "INSERT INTO semesters(name) VALUES (?) ON CONFLICT(name) DO NOTHING RETURNING id",
            ("Học kỳ mẫu",),
        ).fetchone()
        if semester is not None:
            db.executemany(
                """INSERT INTO courses(semester_id, code, name, credits, process_1, process_2, midterm, final)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                [(semester["id"], "SQL101", "Cơ sở dữ liệu", 3, 700, 800, 700, 900),
                 (semester["id"], "PY101", "Python", 2, 700, 700, 700, 700)],
            )


def add_semester(db, name):
    with db:
        return db.execute("INSERT INTO semesters(name) VALUES (?)", (name.strip(),)).lastrowid


def semesters(db):
    return db.execute("SELECT id, name FROM semesters ORDER BY id").fetchall()


def add_course(db, semester_id, code, name, credits):
    with db:
        return db.execute(
            "INSERT INTO courses(semester_id,code,name,credits) VALUES (?, ?, ?, ?)",
            (semester_id, code.strip().upper(), name.strip(), credits),
        ).lastrowid


def courses(db, semester_id):
    return db.execute(
        "SELECT * FROM courses WHERE semester_id = ? ORDER BY id", (semester_id,)
    ).fetchall()


def set_grades(db, course_id, grades):
    with db:
        changed = db.execute(
            """UPDATE courses SET process_1 = ?, process_2 = ?, midterm = ?, final = ?
               WHERE id = ?""",
            (*grades, course_id),
        ).rowcount
        if not changed:
            raise ValueError("Không tìm thấy môn học")


def parse_grade(text):
    text = text.strip().replace(",", ".")
    if not text:
        return None
    if not re.fullmatch(r"[0-9]{1,2}(?:\.[0-9]{1,2})?", text):
        raise ValueError("Nhập điểm từ 0 đến 10, tối đa hai chữ số thập phân")
    whole, _, fractional = text.partition(".")
    points = int(whole) * 100 + int(fractional.ljust(2, "0"))
    if points > 1000:
        raise ValueError("Nhập điểm từ 0 đến 10")
    return points


def course_score(grades):
    grades = tuple(grades)
    if len(grades) != len(WEIGHTS):
        raise ValueError("Cần đúng bốn đầu điểm")
    if None in grades:
        return None
    return Fraction(sum(grade * weight for grade, weight in zip(grades, WEIGHTS)), 10000)


def semester_gpa(rows):
    credits = 0
    total = Fraction()
    for row in rows:
        score = course_score(row[field] for field in GRADE_FIELDS)
        if score is None:
            return None
        credits += row["credits"]
        total += score * row["credits"]
    return total / credits if credits else None


def classify(score):
    if score >= 8:
        return "Giỏi"
    if score >= 6:
        return "Khá"
    if score >= 5:
        return "Trung bình"
    return "Kém"


def format_score(score):
    if score is None:
        return "—"
    value = Fraction(score) * 100
    rounded = (2 * value.numerator + value.denominator) // (2 * value.denominator)
    return f"{rounded // 100},{rounded % 100:02d}"
