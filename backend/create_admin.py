import getpass

import bcrypt

from app.repositories import Repository


if __name__ == '__main__':
    user = input('Usuario administrador: ').strip()
    name = input('Nombre: ').strip()
    password = getpass.getpass('Contrasena: ')
    if not user or not name or len(password) < 8:
        raise SystemExit('Se requiere usuario, nombre y una contrasena de al menos 8 caracteres.')
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        raise SystemExit('La contrasena supera el limite de bcrypt: usa como maximo 72 bytes en UTF-8.')
    # bcrypt produce un hash con sal; la contraseña original nunca se almacena.
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode()
    print(Repository.call('sp_usuario_crear', user, name, hashed))
