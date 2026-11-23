"""Menu tiếng Việt cho một học kỳ đang được chọn."""

from fractions import Fraction
import sqlite3

from gpa_lab import (
    GRADE_FIELDS, WEIGHTS, add_course, add_semester, classify, course_score,
    courses, format_score, parse_grade, semester_gpa, semesters, set_grades,
)

GRADE_LABELS = ("Quá trình 1", "Quá trình 2", "Giữa kỳ", "Cuối kỳ")


def choose(rows, label):
    print("0. Quay lại")
    choice = int(input(f"Chọn {label}: ").strip())
    if choice == 0:
        return None
    if not 1 <= choice <= len(rows):
        raise ValueError(f"Số thứ tự {label} không hợp lệ")
    return rows[choice - 1]


def select_semester(db):
    rows = semesters(db)
    if not rows:
        print("Hãy thêm học kỳ trước.")
        return None
    for index, row in enumerate(rows, 1):
        print(f"{index}. {row['name']}")
    return choose(rows, "học kỳ")


def create_course(db, semester_id):
    code = input("Mã môn: ")
    name = input("Tên môn: ")
    credits = int(input("Số tín chỉ (số nguyên dương): ").strip())
    add_course(db, semester_id, code, name, credits)
    print("Đã thêm môn.")


def format_grade(grade):
    return format_score(None if grade is None else Fraction(grade, 100))


def edit_grades(db, semester_id):
    rows = courses(db, semester_id)
    if not rows:
        print("Hãy thêm môn trước.")
        return
    for index, row in enumerate(rows, 1):
        print(f"{index}. {row['code']} — {row['name']}")
    course = choose(rows, "môn")
    if course is None:
        return
    print("Nhập = để giữ điểm cũ, bỏ trống để đánh dấu chưa nhập.")
    grades = []
    for label, field, weight in zip(GRADE_LABELS, GRADE_FIELDS, WEIGHTS):
        old = course[field]
        while True:
            text = input(f"{label} ({weight}%) [{format_grade(old)}]: ").strip()
            try:
                grades.append(old if text == "=" else parse_grade(text))
                break
            except ValueError as error:
                print(error)
    set_grades(db, course["id"], tuple(grades))
    print("Đã lưu điểm.")


def show_results(db, semester_id):
    rows = courses(db, semester_id)
    if rows:
        headings = (*(
            f"{label} ({weight}%)" for label, weight in zip(GRADE_LABELS, WEIGHTS)
        ), "Điểm môn", "Điểm × tín chỉ")
        print(" | ".join(("Mã môn", "Tên môn", "Tín chỉ", *headings)))
        for row in rows:
            grades = tuple(row[field] for field in GRADE_FIELDS)
            score = course_score(grades)
            weighted = None if score is None else score * row["credits"]
            print(" | ".join((
                row["code"], row["name"], str(row["credits"]),
                *(format_grade(grade) for grade in grades),
                format_score(score), format_score(weighted),
            )))
            missing = [label for label, grade in zip(GRADE_LABELS, grades) if grade is None]
            if missing:
                print(f"  Cần bổ sung {', '.join(missing)}.")
        print(f"Tổng tín chỉ trong kỳ: {sum(row['credits'] for row in rows)}")
    else:
        print("Học kỳ chưa có môn.")
    gpa = semester_gpa(rows)
    if gpa is None:
        print("Chưa đủ dữ liệu tính GPA học kỳ")
    else:
        print(f"GPA học kỳ (thang 10): {format_score(gpa)} — {classify(gpa)}")
        print("Xếp loại được tính trước khi làm tròn.")


def run_menu(db):
    existing = semesters(db)
    current = existing[0] if existing else None
    while True:
        print(f"\nHọc kỳ: {current['name'] if current is not None else 'Chưa chọn'}")
        print("1. Thêm học kỳ\n2. Chọn học kỳ\n3. Thêm môn")
        print("4. Nhập hoặc sửa điểm\n5. Xem kết quả\n0. Thoát")
        try:
            action = input("Chọn mục: ").strip()
            if action == "0":
                return
            if action == "1":
                name = input("Tên học kỳ: ").strip()
                semester_id = add_semester(db, name)
                current = {"id": semester_id, "name": name}
            elif action == "2":
                selected = select_semester(db)
                if selected is not None:
                    current = selected
            elif action in {"3", "4", "5"}:
                if current is None:
                    print("Hãy thêm hoặc chọn học kỳ trước.")
                    continue
                handler = {"3": create_course, "4": edit_grades, "5": show_results}[action]
                handler(db, current["id"])
            else:
                print("Chọn một mục từ 0 đến 5.")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        except sqlite3.IntegrityError:
            print("Dữ liệu không hợp lệ. Kiểm tra tên kỳ, mã môn và số tín chỉ.")
        except OverflowError:
            print("Số tín chỉ quá lớn.")
        except ValueError as error:
            print(error if not str(error).startswith("invalid literal for int()") else
                  "Vui lòng nhập một số nguyên.")

