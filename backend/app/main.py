from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas import CategoriaNueva, Login, MovimientoNuevo, ProductoDatos
from app.services import execute, login, user_from_token

app = FastAPI(title='TecnoStock API')
bearer = HTTPBearer()


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    return user_from_token(credentials.credentials)


@app.post('/api/auth/login')
def authenticate(body: Login):
    return login(body.usuario, body.contrasena)


@app.get('/api/categorias')
def categories(_: int = Depends(current_user)):
    return execute('sp_categoria_listar')


@app.post('/api/categorias', status_code=201)
def create_category(body: CategoriaNueva, _: int = Depends(current_user)):
    return execute('sp_categoria_crear', body.nombre.strip(), body.descripcion.strip())[0]


@app.get('/api/productos')
def products(buscar: str | None = None, id_categoria: int | None = None,
             solo_bajo: bool = False, solo_activos: bool = True, _: int = Depends(current_user)):
    return execute('sp_producto_listar', buscar or None, id_categoria, solo_bajo, solo_activos)


@app.get('/api/productos/{id_producto}')
def product(id_producto: int, _: int = Depends(current_user)):
    rows = execute('sp_producto_obtener', id_producto)
    if not rows:
        raise HTTPException(404, 'Producto no encontrado')
    return rows[0]


def product_parameters(body: ProductoDatos):
    return (body.codigo.strip(), body.nombre.strip(), body.descripcion.strip(), body.id_categoria,
            body.precio_compra, body.precio_venta, body.stock_minimo)


@app.post('/api/productos', status_code=201)
def create_product(body: ProductoDatos, _: int = Depends(current_user)):
    return execute('sp_producto_crear', *product_parameters(body))[0]


@app.put('/api/productos/{id_producto}')
def update_product(id_producto: int, body: ProductoDatos, _: int = Depends(current_user)):
    execute('sp_producto_actualizar', id_producto, *product_parameters(body))
    return product(id_producto, _)


@app.delete('/api/productos/{id_producto}')
def deactivate_product(id_producto: int, _: int = Depends(current_user)):
    execute('sp_producto_desactivar', id_producto)
    return {'mensaje': 'Producto desactivado'}


@app.post('/api/movimientos', status_code=201)
def create_movement(body: MovimientoNuevo, user_id: int = Depends(current_user)):
    return execute('sp_movimiento_registrar', body.id_producto, user_id, body.tipo,
                   body.cantidad, body.fecha, body.motivo.strip())[0]


@app.get('/api/movimientos')
def movements(id_producto: int | None = None, desde: datetime | None = None,
              hasta: datetime | None = None, _: int = Depends(current_user)):
    if desde and hasta and desde > hasta:
        raise HTTPException(400, 'El rango de fechas es invalido')
    return execute('sp_movimiento_listar', id_producto, desde, hasta)


@app.get('/api/indicadores')
def indicators(_: int = Depends(current_user)):
    return execute('sp_indicadores')[0]
