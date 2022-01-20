from typing import List


class ConfigLineParser:
    _current_value: str
    _values: List[str]
    _in_quotes: bool
    _is_escaped: bool
    _character_handler_map: dict

    def __init__(self):
        self._character_handler_map = {
            '"': self._handle_quoting,
            '\\': self._handle_escaping,
            ' ': self._handle_whitespace,
        }

    def parse_values_from_line(self, line: str) -> List[str]:
        self._current_value = ''
        self._values = []
        self._is_escaped = False
        self._in_quotes = False

        for character in line:
            self._parse_character(character)

        self._flush_value()

        return self._values

    def _parse_character(self, character: str):
        if character in self._character_handler_map:
            self._character_handler_map[character]()
        else:
            self._append_character(character)

    def _handle_whitespace(self):
        if self._in_quotes:
            self._append_character(' ')
        else:
            self._flush_value()

    def _handle_quoting(self):
        if self._is_escaped:
            self._append_character('"')
        else:
            self._in_quotes = not self._in_quotes
            self._flush_value()

    def _handle_escaping(self):
        if not self._in_quotes or self._is_escaped:
            # backslashes are only written when _is_escaped is True and _append_character is called
            # as there is not escaping when not in quotes and there is the special case of two backslashes
            # append a backslash here
            self._append_character('\\')
        self._is_escaped = self._in_quotes

    def _append_character(self, character: str):
        if self._is_escaped and character not in ['"', '\\']:
            self._current_value = f'{self._current_value}\\{character}'
        else:
            self._current_value = f'{self._current_value}{character}'

        self._is_escaped = False

    def _flush_value(self):
        self._append_character('')  # add trailing backslash in case it got forgotten
        self._is_escaped = False

        if self._current_value:
            self._values.append(self._current_value)
            self._current_value = ''
