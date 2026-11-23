from contextlib import closing
from fractions import Fraction
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from gpa_lab import (
    add_course, add_semester, classify, course_score, courses, format_score,
    open_db, parse_grade, semester_gpa, set_grades,
)


class GPATests(unittest.TestCase):
    def test_course_weights(self):
        for index, expected in enumerate((1, 2, 2, 5)):
            with self.subTest(component=index):
                grades = [0, 0, 0, 0]
                grades[index] = 1000
                self.assertEqual(course_score(grades), expected)
        self.assertEqual(course_score((700, 800, 700, 900)), Fraction(820, 100))

    def test_classification_boundaries(self):
        for points, expected in (
            (499, "Kém"), (500, "Trung bình"), (599, "Trung bình"),
            (600, "Khá"), (799, "Khá"), (800, "Giỏi"),
        ):
            with self.subTest(points=points):
                self.assertEqual(classify(Fraction(points, 100)), expected)
        self.assertEqual(classify(Fraction(7999, 1000)), "Khá")
        self.assertEqual(format_score(Fraction(7999, 1000)), "8,00")

    def test_input(self):
        self.assertEqual(parse_grade(" 8,25 "), 825)
        self.assertEqual(parse_grade("0"), 0)
        self.assertIsNone(parse_grade(""))
        for text in ("-0.01", "10.01", "8.255"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_grade(text)

    def test_sample_and_persistence(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "gpa.db"
            with closing(open_db(path, sample=True)) as db:
                self.assertEqual(semester_gpa(courses(db, 1)), Fraction(772, 100))
                course = courses(db, 1)[0]["id"]
                set_grades(db, course, (None, 800, 700, 900))
                self.assertIsNone(semester_gpa(courses(db, 1)))
            with closing(open_db(path, sample=True)) as db:
                self.assertEqual(len(courses(db, 1)), 2)
                self.assertIsNone(semester_gpa(courses(db, 1)))
                set_grades(db, course, (0, 800, 700, 900))
                self.assertEqual(semester_gpa(courses(db, 1)), Fraction(73, 10))
            with closing(open_db(path)) as db:
                self.assertEqual(semester_gpa(courses(db, 1)), Fraction(73, 10))

    def test_empty_semester_and_course_uniqueness(self):
        with closing(open_db(":memory:")) as db:
            first = add_semester(db, "Kỳ 1")
            second = add_semester(db, "Kỳ 2")
            self.assertIsNone(semester_gpa(courses(db, first)))
            add_course(db, first, "SQL101", "SQL", 3)
            add_course(db, second, "SQL101", "SQL", 3)
            with self.assertRaises(sqlite3.IntegrityError):
                add_course(db, first, "sql101", "SQL", 3)
            with self.assertRaises(sqlite3.IntegrityError):
                add_course(db, 99, "PY101", "Python", 2)

