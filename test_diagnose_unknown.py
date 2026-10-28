import unittest
from diagnose_unknown import decode


class DecodeTests(unittest.TestCase):
    def test_explicit_abstention_is_distinct_from_invalid(self):
        self.assertEqual(decode('{"answer":"UNKNOWN"}', ['A', 'B']), 'UNKNOWN')
        self.assertEqual(decode('{"answer":"C"}', ['A', 'B']), 'INVALID')
        self.assertEqual(decode('broken', ['A', 'B']), 'INVALID')

    def test_plain_label_does_not_guess_from_prose(self):
        self.assertEqual(decode(' B\n', ['A', 'B'], True), 'B')
        self.assertEqual(decode('UNKNOWN', ['A', 'B'], True), 'UNKNOWN')
        self.assertEqual(decode('I think B', ['A', 'B'], True), 'INVALID')


if __name__ == '__main__':
    unittest.main()

