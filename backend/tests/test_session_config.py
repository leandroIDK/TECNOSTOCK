import os
import unittest
from unittest.mock import patch

import bcrypt
from fastapi import HTTPException

from app.services import login
from app.session_config import session_settings


class SessionConfigTests(unittest.TestCase):
    def test_missing_jwt_secret_is_reported(self):
        with patch.dict(os.environ, {'JWT_SECRET': ''}):
            with self.assertRaisesRegex(ValueError, 'JWT_SECRET'):
                session_settings()

    def test_login_with_valid_password_reports_missing_config(self):
        hashed = bcrypt.hashpw(b'claveSegura123', bcrypt.gensalt()).decode()
        account = {'id_usuario': 1, 'nombre': 'Ana', 'activo': True, 'hash_contrasena': hashed}
        with patch('app.services.execute', return_value=[account]), patch.dict(os.environ, {'JWT_SECRET': ''}):
            with self.assertRaises(HTTPException) as error:
                login('ana', 'claveSegura123')
        self.assertEqual(error.exception.status_code, 503)

    def test_valid_settings(self):
        with patch.dict(os.environ, {'JWT_SECRET': 'x' * 32, 'JWT_EXP_MINUTES': '60'}):
            self.assertEqual(session_settings(), ('x' * 32, 60))


if __name__ == '__main__':
    unittest.main()
