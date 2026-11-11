import unittest
from unittest.mock import patch

import bcrypt
from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas import RegistroUsuario
from app.services import register_user


class RegistrationTests(unittest.TestCase):
    def test_uses_bcrypt_hash_and_not_plain_password(self):
        body = RegistroUsuario(dni='12345678', nombre=' Ana ', apellido=' Vega ',
                               usuario='ana_vega', contrasena='claveSegura123')
        with patch('app.services.execute', return_value=[{'id_usuario': 99}]) as execute:
            result = register_user(body)
        self.assertEqual(result['id_usuario'], 99)
        args = execute.call_args.args
        self.assertEqual(args[:5], ('sp_usuario_registrar', '12345678', 'Ana', 'Vega', 'ana_vega'))
        self.assertNotEqual(args[5], body.contrasena)
        self.assertTrue(bcrypt.checkpw(body.contrasena.encode(), args[5].encode()))

    def test_rejects_invalid_dni(self):
        with self.assertRaises(ValidationError):
            RegistroUsuario(dni='123', nombre='Ana', apellido='Vega',
                            usuario='ana_vega', contrasena='claveSegura123')

    def test_rejects_password_over_bcrypt_limit(self):
        body = RegistroUsuario(dni='12345678', nombre='Ana', apellido='Vega',
                               usuario='ana_vega', contrasena='a' * 73)
        with self.assertRaises(HTTPException) as error:
            register_user(body)
        self.assertEqual(error.exception.status_code, 422)


if __name__ == '__main__':
    unittest.main()
