import logging
import os
import unittest
from typing import List

from doxygen import ConfigParser


class DoxygenConfigParserTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(DoxygenConfigParserTest, self).__init__(*args, **kwargs)
        logging.disable(logging.CRITICAL)
        self.doxyfile_original = os.path.join(os.path.dirname(__file__), "assets/Doxyfile")
        self.doxyfile_working = "./Doxyfile.tmp"
        self.doxyfile_clone = "./Cloned_Doxyfile.tmp"

    def test_try_use_not_existing_doxyfile(self):
        config_parser = ConfigParser()
        self.assertRaises(FileNotFoundError, config_parser.load_configuration, "./NotExisting/file/Doxyfile")

    def tearDown(self):
        if os.path.exists(self.doxyfile_working):
            os.remove(self.doxyfile_working)

        if os.path.exists(self.doxyfile_clone):
            os.remove(self.doxyfile_clone)

    def test_load_configuration(self):
        config_parser = ConfigParser()
        configuration = config_parser.load_configuration(self.doxyfile_original)
        self.assertIsInstance(configuration, dict)
        self.assertEqual(len(configuration), 270)

    def test_update_configuration(self):
        config_parser = ConfigParser()

        configuration = config_parser.load_configuration(self.doxyfile_original)
        self.assertTrue('PROJECT_NAME' in configuration)
        self.assertTrue('PROJECT_NUMBER' in configuration)
        self.assertTrue('FILE_PATTERNS' in configuration)

        configuration['PROJECT_NAME'] = 'something cool'
        configuration['PROJECT_NUMBER'] = '1.2.3.4'
        configuration['FILE_PATTERNS'].append("*.dtc")

        config_parser.store_configuration(configuration, self.doxyfile_working)

        configuration_updated = config_parser.load_configuration(self.doxyfile_working)
        self.assertTrue('PROJECT_NAME' in configuration_updated)
        self.assertTrue('PROJECT_NUMBER' in configuration_updated)
        self.assertTrue('FILE_PATTERNS' in configuration_updated)

        self.assertEqual(configuration_updated['PROJECT_NAME'], 'something cool')
        self.assertEqual(configuration_updated['PROJECT_NUMBER'], '1.2.3.4')
        self.assertTrue("*.dtc" in configuration_updated['FILE_PATTERNS'])

    def test_multiline_option_with_empty_lines(self):
        configuration = self.get_configuration_from_lines([
            'MULTILINE_OPTION = \\',
            '                   \\',
            '                   line3',
        ])

        self.assertEqual('line3', configuration['MULTILINE_OPTION'])

    def test_multiline_option(self):
        configuration = self.get_configuration_from_lines([
            'MULTILINE_OPTION = line1 \\',
            '                   line2 \\',
            '                   line3',
        ])

        self.assertEqual(['line1', 'line2', 'line3'], configuration['MULTILINE_OPTION'])

    def test_quoted_multiline_option(self):
        configuration = self.get_configuration_from_lines([
            'MULTILINE_OPTION = "line 1" \\',
            '                   "line 2" \\',
            '                   "line 3"',
        ])

        self.assertEqual(['line 1', 'line 2', 'line 3'], configuration['MULTILINE_OPTION'])

    def get_configuration_from_lines(self, lines: List[str]) -> dict:
        """Writes lines into a Doxyfile and reads it. This will also write and load the configuration again to check if
        the config_parser changes it
        """
        with open(self.doxyfile_working, 'w') as io:
            io.write('\n'.join(lines))

        parser = ConfigParser()
        configuration = parser.load_configuration(self.doxyfile_working)
        parser.store_configuration(configuration, self.doxyfile_clone)
        other_configuration = parser.load_configuration(self.doxyfile_clone)
        self.assertEqual(configuration, other_configuration)
        return configuration

    def test_multiple_values_in_one_line(self):
        configuration = self.get_configuration_from_lines([
            'OPTION = value1 value2 value3'
        ])

        self.assertEqual(['value1', 'value2', 'value3'], configuration['OPTION'])

    def test_multiple_values_in_one_line_with_quotes(self):
        configuration = self.get_configuration_from_lines([
            'OPTION = "value1" "value2" "value3"'
        ])

        self.assertEqual(['value1', 'value2', 'value3'], configuration['OPTION'])

    def test_multiple_values_in_multiple_lines(self):
        configuration = self.get_configuration_from_lines([
            'OPTION = "value 1" value2 \\',
            '         "value 3" value4',
        ])

        self.assertEqual(['value 1', 'value2', 'value 3', 'value4'], configuration['OPTION'])

    def test_quote_escaping(self):
        configuration = self.get_configuration_from_lines([
            'OPTION = "escaped quote \\""',
        ])

        self.assertEqual('escaped quote "', configuration['OPTION'])

    def test_escaped_quote_in_multiline_option(self):
        configuration = self.get_configuration_from_lines([
            'OPTION = "first escaped quote \\"" \\',
            '         "second escaped quote \\""',
        ])

        self.assertEqual(['first escaped quote "', 'second escaped quote "'], configuration['OPTION'])

    def test_crazy_escaped_quote_outside_of_quotes(self):
        configuration = self.get_configuration_from_lines([
            'OPTION = escaped quote outside of value \\"remaining line',
        ])

        self.assertEqual(['escaped', 'quote', 'outside', 'of', 'value', '\\', 'remaining line'],
                         configuration['OPTION'])


if __name__ == '__main__':
    unittest.main()
