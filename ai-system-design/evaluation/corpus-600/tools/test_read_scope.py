import unittest

from audit_read_scope import coverage_mask, quote_is_read


class ReadingScopeTests(unittest.TestCase):
    def test_producer_coordinate_formats_preserve_crlf(self):
        text = 'title\r\nread this\r\nunread suffix\r\n'
        for scope in [
            {'read_line_intervals': [[2, 2]]},
            {'line_character_intervals': [{'line': 2, 'start_char': 0, 'end_char': 9}]},
            {'character_intervals': [[7, 16]]},
        ]:
            mask = coverage_mask(text, scope)
            self.assertTrue(quote_is_read(text, 'read this', mask))
            self.assertFalse(quote_is_read(text, 'read this\r\nunread', mask))

    def test_repeated_phrase_requires_a_read_occurrence(self):
        text = 'duplicate\nother\nduplicate\n'
        mask = coverage_mask(text, {'intervals': [[3, 3]]})
        self.assertTrue(quote_is_read(text, 'duplicate', mask))
        self.assertFalse(quote_is_read(text, 'other\nduplicate', mask))
        with self.assertRaises(ValueError):
            coverage_mask(text, {'character_intervals': [[0, len(text) + 1]]})


if __name__ == '__main__':
    unittest.main()
