import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import pyodbc
from fastapi import HTTPException

from app.repositories import Repository
from app.schemas import RegistroUsuario


def execute(procedure, *parameters):
    try:
        return Repository.call(procedure, *parameters)
    except pyodbc.Error as exc:
        message = str(exc)
        if '50007' in message:
            raise HTTPException(409, 'Stock insuficiente') from exc
        if '50005' in message:
            raise HTTPException(404, 'Producto activo no encontrado') from exc
        if '2601' in message or '2627' in message:
            raise HTTPException(409, 'Ya existe un registro con ese codigo o nombre') from exc
        if '547' in message:
            raise HTTPException(400, 'La categoria o el usuario no existe') from exc
        if any(str(code) in message for code in range(50001, 50007)):
            raise HTTPException(400, 'Datos invalidos') from exc
        if '50009' in message or '50010' in message:
            raise HTTPException(400, 'Datos de registro invalidos') from exc
        raise HTTPException(503, 'No se pudo completar la operacion de base de datos') from exc


def register_user(body: RegistroUsuario):
    password_bytes = body.contrasena.encode('utf-8')
    if len(password_bytes) > 72:
        raise HTTPException(422, 'La contrasena supera el limite de 72 bytes de bcrypt')
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode()
    try:
        result = execute('sp_usuario_registrar', body.dni, body.nombre, body.apellido,
                         body.usuario, password_hash)[0]
    except HTTPException as exc:
        if exc.status_code == 409:
            raise HTTPException(409, 'El usuario o DNI ya esta registrado') from exc
        raise
    return result


def login(usuario: str, contrasena: str):
    rows = execute('sp_usuario_por_nombre', usuario.strip())
    password_bytes = contrasena.encode('utf-8')
    if (not rows or not rows[0]['activo'] or len(password_bytes) > 72
            or not bcrypt.checkpw(password_bytes, rows[0]['hash_contrasena'].encode())):
        raise HTTPException(401, 'Credenciales incorrectas')
    secret = os.getenv('JWT_SECRET')
    if not secret:
        raise RuntimeError('Falta JWT_SECRET')
    expires = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv('JWT_EXP_MINUTES', '120')))
    token = jwt.encode({'sub': str(rows[0]['id_usuario']), 'exp': expires}, secret, algorithm='HS256')
    return {'access_token': token, 'token_type': 'bearer', 'nombre': rows[0]['nombre']}


def user_from_token(token: str):
    try:
        payload = jwt.decode(token, os.environ['JWT_SECRET'], algorithms=['HS256'])
        return int(payload['sub'])
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise HTTPException(401, 'Sesion invalida o vencida') from exc
