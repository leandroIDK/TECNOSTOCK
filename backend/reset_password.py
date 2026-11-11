from app.repositories import Repository
from password_input import new_password_hash


if __name__ == '__main__':
    username = input('Usuario de la aplicacion: ').strip()
    if not username or not Repository.call('sp_usuario_por_nombre', username):
        raise SystemExit('No existe ese usuario.')
    hashed = new_password_hash()
    Repository.call('sp_usuario_cambiar_hash', username, hashed)
    print('Contrasena actualizada.')
