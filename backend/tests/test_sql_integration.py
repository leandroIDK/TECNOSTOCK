"""Prueba opcional contra SQL Server: TECNOSTOCK_DB_TEST=1. Revierte todos sus datos."""

import os
import secrets
import unittest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import bcrypt
import pyodbc

from app.db import connection
from app.repositories import Repository


@unittest.skipUnless(os.getenv('TECNOSTOCK_DB_TEST') == '1', 'Requiere SQL Server de prueba')
class SqlIntegrationTests(unittest.TestCase):
    def test_exit_cannot_make_stock_negative(self):
        suffix = uuid4().hex[:10]
        username = f'prueba_{suffix}'
        code = f'TEST-{suffix}'
        dni = f'{secrets.randbelow(90_000_000) + 10_000_000:08d}'
        with connection() as db:
            db.autocommit = False
            cursor = db.cursor()

            def call(name, *values):
                cursor.execute(f'EXEC dbo.{name} {",".join("?" for _ in values)}', values)
                return cursor.fetchall() if cursor.description else []

            try:
                user_id = call('sp_usuario_registrar', dni, 'Prueba', 'Salida', username,
                               bcrypt.hashpw(b'claveSegura123', bcrypt.gensalt()).decode())[0][0]
                category_id = call('sp_categoria_crear', f'Categoria {suffix}', 'Prueba reversible')[0][0]
                product_id = call('sp_producto_crear', code, 'Producto de prueba', '', category_id,
                                  Decimal('10.00'), Decimal('15.00'), 1)[0][0]
                call('sp_movimiento_registrar', product_id, user_id, 'ENTRADA', 3,
                     datetime.now(), 'Entrada de prueba')
                with self.assertRaises(pyodbc.Error) as error:
                    call('sp_movimiento_registrar', product_id, user_id, 'SALIDA', 4,
                         datetime.now(), 'Salida imposible')
                self.assertIn('50007', str(error.exception))
            finally:
                db.rollback()

        self.assertEqual(Repository.call('sp_usuario_por_nombre', username), [])
        self.assertEqual(Repository.call('sp_producto_listar', code, None, False, False), [])

    def test_registration_products_movements_and_history(self):
        suffix = uuid4().hex[:10]
        username = f'prueba_{suffix}'
        code = f'TEST-{suffix}'
        dni = f'{secrets.randbelow(90_000_000) + 10_000_000:08d}'

        with connection() as db:
            db.autocommit = False
            cursor = db.cursor()

            def call(name, *values):
                placeholders = ','.join('?' for _ in values)
                cursor.execute(f'EXEC dbo.{name} {placeholders}', values)
                if cursor.description is None:
                    return []
                columns = [item[0] for item in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

            try:
                hashed = bcrypt.hashpw(b'claveSegura123', bcrypt.gensalt()).decode()
                user = call('sp_usuario_registrar', dni, 'Prueba', 'Integracion', username, hashed)[0]
                account = call('sp_usuario_por_nombre', username)[0]
                self.assertTrue(bcrypt.checkpw(b'claveSegura123', account['HashContrasena'].encode()))

                category = call('sp_categoria_crear', f'Categoria {suffix}', 'Prueba reversible')[0]
                product = call('sp_producto_crear', code, f'Producto {suffix}', 'Prueba reversible',
                               category['IdCategoria'], Decimal('10.00'), Decimal('15.00'), 3)[0]
                product_id = product['IdProducto']

                entry = call('sp_movimiento_registrar', product_id, user['IdUsuario'],
                             'ENTRADA', 5, datetime.now(), 'Entrada de prueba')[0]
                self.assertEqual((entry['StockAnterior'], entry['StockPosterior']), (0, 5))
                exit_ = call('sp_movimiento_registrar', product_id, user['IdUsuario'],
                             'SALIDA', 2, datetime.now(), 'Salida de prueba')[0]
                self.assertEqual((exit_['StockAnterior'], exit_['StockPosterior']), (5, 3))
                self.assertEqual(call('sp_producto_obtener', product_id)[0]['StockActual'], 3)
                self.assertEqual(len(call('sp_movimiento_listar', product_id, None, None)), 2)
                self.assertEqual(len(call('sp_producto_listar', code, category['IdCategoria'], True, True)), 1)

                call('sp_producto_actualizar', product_id, code, f'Producto editado {suffix}',
                     'Descripcion editada', category['IdCategoria'], Decimal('11.00'), Decimal('16.00'), 3)
                self.assertEqual(call('sp_producto_obtener', product_id)[0]['PrecioCompra'], Decimal('11.00'))
                call('sp_producto_desactivar', product_id)
                self.assertEqual(call('sp_producto_listar', code, None, False, True), [])
                self.assertEqual(len(call('sp_movimiento_listar', product_id, None, None)), 2)
            finally:
                db.rollback()

        self.assertEqual(Repository.call('sp_usuario_por_nombre', username), [])
        self.assertEqual(Repository.call('sp_producto_listar', code, None, False, False), [])


if __name__ == '__main__':
    unittest.main()
