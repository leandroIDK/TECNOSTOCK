from app.db import connection, snake


class Repository:
    # Toda lectura y escritura de datos se hace exclusivamente con procedimientos almacenados.
    @staticmethod
    def call(procedure: str, *parameters):
        allowed = {
            'sp_usuario_crear', 'sp_usuario_por_nombre', 'sp_usuario_cambiar_hash',
            'sp_usuario_registrar',
            'sp_categoria_crear', 'sp_categoria_listar',
            'sp_producto_crear', 'sp_producto_actualizar', 'sp_producto_desactivar',
            'sp_producto_listar', 'sp_producto_obtener',
            'sp_movimiento_registrar', 'sp_movimiento_listar', 'sp_indicadores',
            'sp_demo_cargar',
        }
        if procedure not in allowed:
            raise ValueError('Procedimiento no permitido')
        placeholders = ','.join('?' for _ in parameters)
        with connection() as db:
            cursor = db.cursor()
            cursor.execute(f'EXEC dbo.{procedure} {placeholders}', parameters)
            if cursor.description is None:
                return []
            names = [snake(column[0]) for column in cursor.description]
            return [dict(zip(names, row)) for row in cursor.fetchall()]
