"""
Unit tests for PDF Parsing Engine.
"""

import unittest
from backend.academic_engine.parser import CourseDetector, PDFParser, SectionDetector, TextCleaner


class TestPDFParsingEngine(unittest.TestCase):
    """Test suite for TextCleaner, SectionDetector, CourseDetector, and PDFParser."""

    def setUp(self):
        self.sample_text = """
        Stanford University
        Department of Computer Science
        Course Syllabus 2025-2026

        CS101: Introduction to Data Structures and Algorithms
        Credits: 4.0
        Semester 1

        Course Overview
        This course introduces fundamental data structures using Python, C++, and Java.

        Learning Outcomes
        - Implement binary search trees and hash maps.
        - Analyze asymptotic complexity of algorithms.

        Course Content
        Module 1: Array, Linked List, and Queue
        Module 2: Binary Search Trees and Graphs
        """

    def test_text_cleaner(self):
        cleaned = TextCleaner.clean("Page 1 of 5\n\n\nHeader  Text   here  ")
        self.assertNotIn("Page 1 of 5", cleaned)
        self.assertIn("Header Text here", cleaned)

    def test_section_detector(self):
        sections = SectionDetector.detect_sections(self.sample_text)
        self.assertTrue(len(sections) >= 3)
        section_types = [s.section_type for s in sections]
        self.assertIn("overview", section_types)
        self.assertIn("outcomes", section_types)

    def test_course_detector(self):
        courses = CourseDetector.detect_courses(self.sample_text)
        self.assertTrue(len(courses) > 0)
        self.assertEqual(courses[0].course_code, "CS101")
        self.assertEqual(courses[0].credits, 4.0)

    def test_pdf_parser_fallback(self):
        parser = PDFParser()
        doc = parser.parse_pdf(file_source=self.sample_text.encode("utf-8"), document_id="doc-test-1")
        self.assertEqual(doc.document_id, "doc-test-1")
        self.assertTrue(len(doc.sections) > 0)
        self.assertTrue(len(doc.courses) > 0)


if __name__ == "__main__":
    unittest.main()
