import unittest
import os
from unittest.mock import patch

import bcrypt
import jwt
from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas import RegistroUsuario
from app.services import login, register_user


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

    def test_new_account_can_login_with_same_password(self):
        body = RegistroUsuario(dni='12345678', nombre='Ana', apellido='Vega',
                               usuario='ana_vega', contrasena='claveSegura123')
        saved = {}

        def procedure(name, *args):
            if name == 'sp_usuario_registrar':
                saved['hash'] = args[4]
                return [{'id_usuario': 99}]
            if name == 'sp_usuario_por_nombre':
                return [{'id_usuario': 99, 'nombre': 'Ana', 'activo': True,
                         'hash_contrasena': saved['hash']}]
            raise AssertionError(name)

        with patch('app.services.execute', side_effect=procedure), patch.dict(
                os.environ, {'JWT_SECRET': 'x' * 32, 'JWT_EXP_MINUTES': '60'}):
            register_user(body)
            result = login('ana_vega', 'claveSegura123')
            payload = jwt.decode(result['access_token'], 'x' * 32, algorithms=['HS256'])
        self.assertEqual(payload['sub'], '99')


if __name__ == '__main__':
    unittest.main()
