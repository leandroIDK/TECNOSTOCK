import os


def session_settings() -> tuple[str, int]:
    secret = os.getenv('JWT_SECRET', '')
    if secret == 'generar_una_clave_aleatoria_larga' or len(secret.encode('utf-8')) < 32:
        raise ValueError('Configura JWT_SECRET en backend/.env con al menos 32 bytes aleatorios.')
    try:
        minutes = int(os.getenv('JWT_EXP_MINUTES', '120'))
    except ValueError as exc:
        raise ValueError('JWT_EXP_MINUTES debe ser un numero entero positivo.') from exc
    if minutes <= 0:
        raise ValueError('JWT_EXP_MINUTES debe ser un numero entero positivo.')
    return secret, minutes
