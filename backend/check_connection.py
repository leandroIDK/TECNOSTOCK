from app.repositories import Repository
from app.session_config import session_settings


if __name__ == '__main__':
    result = Repository.call('sp_indicadores')
    print('Conexión correcta con TecnoStock. Indicadores:', result[0])
    try:
        session_settings()
    except ValueError as exc:
        raise SystemExit(f'Configuracion de inicio de sesion pendiente: {exc}') from exc
    print('Configuracion de inicio de sesion correcta.')
