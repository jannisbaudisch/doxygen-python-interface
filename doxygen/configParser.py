import logging
import os
import re
from typing import List, AnyStr

from doxygen._configLineParser import ConfigLineParser
from doxygen.exceptions import ParseException


class ConfigParser:
    """
    This class should be used to parse and store a doxygen configuration file
    """
    __line_parser: ConfigLineParser

    def __init__(self):
        self.__line_regex = re.compile("^\s*(\w+)\s*=(.*)$")
        self.__line_parser = ConfigLineParser()

    def load_configuration(self, doxyfile: str) -> dict:
        """
        Parse a Doxygen configuration file

        :param doxyfile: Path to the Doxygen configuration file
        :return: A dict with all doxygen configuration
        :raise FileNotFoundError: When doxyfile doesn't exist
        """

        if not os.path.exists(doxyfile) or os.access(doxyfile, os.R_OK):
            logging.error("Impossible to access {}".format(doxyfile))
            raise FileNotFoundError(doxyfile)

        with open(doxyfile, 'r') as file:
            lines = file.readlines()
            return self.load_configuration_lines(lines)

    def load_configuration_lines(self, lines: List[AnyStr]) -> dict:
        configuration = dict()
        in_multiline_option = False
        current_multiline_option_name = None

        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue

            if self.__is_comment_line(line):
                continue

            if in_multiline_option:
                if not line.endswith('\\'):
                    in_multiline_option = False
                value_string = line.rstrip('\\')
                option_values = self.__line_parser.parse_values_from_line(value_string)
                configuration[current_multiline_option_name].extend(option_values)
            elif self.__is_line_with_option(line):
                current_multiline_option_name, value_string, in_multiline_option = self.__extract_line_content(line)
                option_values = self.__line_parser.parse_values_from_line(value_string)
                configuration[current_multiline_option_name] = option_values

        configuration = self.__replace_lists_with_only_one_entry(configuration)

        return configuration

    @staticmethod
    def __replace_lists_with_only_one_entry(configuration: dict):
        for key, value in configuration.items():
            if not value:
                configuration[key] = ''
            if len(value) == 1:
                configuration[key] = value[0]

        return configuration

    def store_configuration(self, config: dict, doxyfile: str):
        """
        Store the doxygen configuration to the disk

        :param config: The doxygen configuration you want to write on disk
        :param doxyfile: The output path where configuration will be written. If the file exist, it will be truncated
        """

        logging.debug("Store configuration in {}".format(doxyfile))

        lines = []
        for option_name, option_value in config.items():
            if type(option_value) is list:
                lines.append("{} = {} \\".format(option_name, self.__add_double_quote_if_required(option_value[0])))
                lines.extend(["\t{} \\".format(self.__add_double_quote_if_required(value)) for value in option_value[1:-1]])
                lines.append("\t{}".format(self.__add_double_quote_if_required(option_value[-1])))
            elif type(option_value) is str:
                lines.append("{} = {}".format(option_name, self.__add_double_quote_if_required(option_value)))

        with open(doxyfile, 'w') as file:
            file.write("\n".join(lines))

    def __extract_line_content(self, line) -> (str, List[str], bool):
        matches = self.__line_regex.search(line)
        if matches is None or len(matches.groups()) != 2:
            logging.error("Impossible to extract value line option from: {}" % line)
            raise ParseException("Impossible to extract value line option from: {}" % line)

        option_name, value_string = matches.groups()

        is_multiline_option = value_string.endswith('\\')
        if is_multiline_option:
            value_string = value_string[:-1]

        return option_name, value_string, is_multiline_option

    def __is_line_with_option(self, line: str) -> bool:
        return self.__line_regex.match(line) is not None

    @staticmethod
    def __is_comment_line(line: str) -> bool:
        return line.startswith("#")

    @staticmethod
    def __add_double_quote_if_required(option_value: str) -> str:
        """
        Add the double quote around string in option value if its required

        :param option_value: The value you want to work on
        :return: The option value proper
        """
        option_value = option_value.replace('"', '\\"')

        if " " in option_value:
            option_value_formatted = '"{}"'.format(option_value)
            logging.debug("Add quote from {} to {}".format(option_value, option_value_formatted))
            return option_value_formatted

        return option_value
