import io
import unittest
from unittest.mock import patch

import bcrypt

from password_input import new_password_hash


class PasswordInputTests(unittest.TestCase):
    def test_asterisks_backspace_and_confirmation(self):
        keys = list('abcx\bdefgh\rabcdefgh\r')
        output = io.StringIO()
        with patch('msvcrt.getwch', side_effect=keys), patch('sys.stdout', output):
            hashed = new_password_hash()
        self.assertTrue(bcrypt.checkpw(b'abcdefgh', hashed.encode()))
        self.assertIn('*', output.getvalue())
        self.assertNotIn('abcdefgh', output.getvalue())

    def test_mismatched_password_is_rejected(self):
        with patch('msvcrt.getwch', side_effect=list('abcdefgh\rabcdegfh\r')):
            with self.assertRaisesRegex(SystemExit, 'no coinciden'):
                new_password_hash()

    def test_password_over_72_bytes_is_rejected(self):
        keys = list('a' * 73 + '\r' + 'a' * 73 + '\r')
        with patch('msvcrt.getwch', side_effect=keys):
            with self.assertRaisesRegex(SystemExit, '72 bytes'):
                new_password_hash()


if __name__ == '__main__':
    unittest.main()
