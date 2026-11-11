from app.repositories import Repository
from password_input import new_password_hash


if __name__ == '__main__':
    user = input('Usuario administrador: ').strip()
    name = input('Nombre: ').strip()
    if not user or not name:
        raise SystemExit('Se requiere usuario y nombre.')
    hashed = new_password_hash()
    print(Repository.call('sp_usuario_crear', user, name, hashed))
