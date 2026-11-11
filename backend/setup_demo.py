import re

from app.repositories import Repository
from password_input import new_password_hash


def required(label: str, limit: int) -> str:
    value = input(f'{label}: ').strip()
    if not value or len(value) > limit:
        raise SystemExit(f'{label} debe tener entre 1 y {limit} caracteres.')
    return value


def main() -> None:
    print('Crea al menos una cuenta para entrar a la web.')
    first_user_id = None

    while True:
        dni = required('DNI (8 digitos)', 8)
        if not re.fullmatch(r'[0-9]{8}', dni):
            raise SystemExit('El DNI debe tener exactamente ocho digitos.')
        name = required('Nombre', 120)
        surname = required('Apellido', 120)
        username = required('Usuario', 80)
        # La clave se solicita en la consola y solo el hash bcrypt llega a SQL Server.
        password_hash = new_password_hash()
        user = Repository.call('sp_usuario_registrar', dni, name, surname,
                               username, password_hash)[0]
        print(f"Usuario creado: {user['usuario']}")
        if first_user_id is None:
            first_user_id = user['id_usuario']

        if input('Crear otro usuario? [s/N]: ').strip().lower() != 's':
            break

    result = Repository.call('sp_demo_cargar', first_user_id)[0]
    print(f"Datos de prueba listos: {result['productos_demo']} productos, "
          f"{result['unidades_demo']} unidades.")


if __name__ == '__main__':
    main()
