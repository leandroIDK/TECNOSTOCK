from app.repositories import Repository


if __name__ == '__main__':
    result = Repository.call('sp_indicadores')
    print('Conexión correcta con TecnoStock. Indicadores:', result[0])
