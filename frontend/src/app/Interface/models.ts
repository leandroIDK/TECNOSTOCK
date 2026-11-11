export interface Category { id_categoria: number; nombre: string; descripcion: string; }
export interface Product {
  id_producto: number; codigo: string; nombre: string; descripcion: string;
  id_categoria: number; categoria: string; precio_compra: number; precio_venta: number;
  stock_minimo: number; stock_actual: number; activo: boolean;
}
export interface ProductInput {
  codigo: string; nombre: string; descripcion: string; id_categoria: number;
  precio_compra: number; precio_venta: number; stock_minimo: number;
}
export interface Movement {
  id_movimiento: number; id_producto: number; codigo: string; producto: string;
  tipo: 'ENTRADA' | 'SALIDA'; cantidad: number; fecha: string; motivo: string;
  stock_anterior: number; stock_posterior: number; usuario: string;
}
export interface Indicators { productos_activos: number; productos_stock_bajo: number; valor_inventario: number; }
export interface RegisterInput {
  dni: string; nombre: string; apellido: string; usuario: string; contrasena: string;
}
