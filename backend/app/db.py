import os
import re
from contextlib import contextmanager

import pyodbc
from dotenv import load_dotenv

load_dotenv()


@contextmanager
def connection():
    auth = os.getenv('DB_AUTH', 'sql').lower()
    if auth not in ('sql', 'windows'):
        raise RuntimeError('DB_AUTH debe ser sql o windows')
    required = ('DB_SERVER', 'DB_NAME') + (('DB_USER', 'DB_PASSWORD') if auth == 'sql' else ())
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError(f'Faltan variables de base de datos: {", ".join(missing)}')
    parts = {
        'DRIVER': os.getenv('DB_DRIVER', 'ODBC Driver 18 for SQL Server'),
        'SERVER': os.environ['DB_SERVER'],
        'DATABASE': os.environ['DB_NAME'],
        'Encrypt': 'yes',
        'TrustServerCertificate': os.getenv('DB_TRUST_CERTIFICATE', 'no'),
    }
    if auth == 'sql':
        parts['UID'] = os.environ['DB_USER']
        parts['PWD'] = os.environ['DB_PASSWORD']
    else:
        parts['Trusted_Connection'] = 'yes'
    value = ';'.join(f'{key}={{{item}}}' for key, item in parts.items()) + ';'
    db = pyodbc.connect(value, autocommit=True)
    try:
        yield db
    finally:
        db.close()


def snake(name: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
