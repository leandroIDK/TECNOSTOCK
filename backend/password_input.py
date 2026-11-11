import getpass
import os

import bcrypt


def _masked_input(prompt: str) -> str:
    if os.name != 'nt':
        return getpass.getpass(prompt)

    import msvcrt

    print(prompt, end='', flush=True)
    characters: list[str] = []
    while True:
        key = msvcrt.getwch()
        if key in ('\r', '\n'):
            print()
            return ''.join(characters)
        if key == '\x03':
            raise KeyboardInterrupt
        if key in ('\x00', '\xe0'):
            msvcrt.getwch()  # Ignora teclas especiales, como las flechas.
        elif key == '\b':
            if characters:
                characters.pop()
                print('\b \b', end='', flush=True)
        elif key.isprintable():
            characters.append(key)
            print('*', end='', flush=True)


def new_password_hash() -> str:
    password = _masked_input('Contrasena (se mostraran asteriscos): ')
    confirmation = _masked_input('Repite la contrasena: ')
    if password != confirmation:
        raise SystemExit('Las contrasenas no coinciden. No se hizo ningun cambio.')
    if len(password) < 8:
        raise SystemExit('La contrasena debe tener al menos 8 caracteres.')
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        raise SystemExit('La contrasena supera el limite de bcrypt: usa como maximo 72 bytes en UTF-8.')
    # bcrypt guarda un hash con sal; la contraseña original no se almacena.
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode()
