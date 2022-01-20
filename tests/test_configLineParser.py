import unittest

from doxygen._configLineParser import ConfigLineParser


class TestConfigLineParser(unittest.TestCase):
    line_parser: ConfigLineParser

    def setUp(self) -> None:
        self.line_parser = ConfigLineParser()

    def test_simple_value(self):
        self.assertEqual(['value1'], self.line_parser.parse_values_from_line('value1'))

    def test_three_values(self):
        self.assertEqual(['value1', 'value2', 'value3'], self.line_parser.parse_values_from_line('value1 value2 value3'))

    def test_ignore_multiple_whitespaces(self):
        self.assertEqual(['value1', 'value2'], self.line_parser.parse_values_from_line('  value1  value2  '))

    def test_quoted_word(self):
        self.assertEqual(['value1'], self.line_parser.parse_values_from_line('"value1"'))

    def test_quoted_words(self):
        self.assertEqual(['value1', 'value2'], self.line_parser.parse_values_from_line('"value1" "value2"'))

    def test_whitespace_in_quoted_word(self):
        self.assertEqual(['value1 value2'], self.line_parser.parse_values_from_line('"value1 value2"'))

    def test_multiple_whitespaces_in_quoted_word(self):
        self.assertEqual(['   value1   value2   '], self.line_parser.parse_values_from_line('  "   value1   value2   "  '))

    def test_escape_quote_in_quotes(self):
        self.assertEqual(['this is a quote "'], self.line_parser.parse_values_from_line('"this is a quote \\""'))

    def test_ignore_other_escapes(self):
        self.assertEqual(['this is an escaped quote \\"'], self.line_parser.parse_values_from_line('"this is an escaped quote \\\\""'))

    def test_escaping_outside_quotes(self):
        self.assertEqual(['value1\\', 'value2'], self.line_parser.parse_values_from_line('value1\\"value2'))

    def test_quotes_start_new_value(self):
        self.assertEqual(['value1', 'value2'], self.line_parser.parse_values_from_line('value1"value2"'))

    def test_quotes_end_value(self):
        self.assertEqual(['value1', 'value2'], self.line_parser.parse_values_from_line('"value1"value2'))
