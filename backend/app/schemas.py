from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class Login(BaseModel):
    usuario: str = Field(min_length=1, max_length=80)
    contrasena: str = Field(min_length=1)


class CategoriaNueva(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str = Field(default='', max_length=400)


class ProductoDatos(BaseModel):
    codigo: str = Field(min_length=1, max_length=40)
    nombre: str = Field(min_length=1, max_length=150)
    descripcion: str = Field(default='', max_length=500)
    id_categoria: int = Field(gt=0)
    precio_compra: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    precio_venta: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    stock_minimo: int = Field(ge=0)


class MovimientoNuevo(BaseModel):
    id_producto: int = Field(gt=0)
    tipo: str = Field(pattern='^(ENTRADA|SALIDA)$')
    cantidad: int = Field(gt=0)
    fecha: datetime
    motivo: str = Field(min_length=1, max_length=400)
