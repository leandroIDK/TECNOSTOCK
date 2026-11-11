import { Component, inject, signal } from '@angular/core';
import { CurrencyPipe, DatePipe } from '@angular/common';
import { FormField, form, maxLength, min, required } from '@angular/forms/signals';
import { HttpErrorResponse } from '@angular/common/http';
import { ApiService } from '../../service/api.service';
import { Category, Indicators, Movement, Product, ProductInput } from '../../Interface/models';

type Section = 'panel' | 'productos' | 'categorias' | 'movimientos' | 'historial' | 'stock-bajo';
type ProductForm = Omit<ProductInput, 'id_categoria'> & { id_categoria: string };
const emptyProduct = (): ProductForm => ({ codigo: '', nombre: '', descripcion: '', id_categoria: '',
  precio_compra: 0, precio_venta: 0, stock_minimo: 0 });
const todayLocal = () => {
  const date = new Date();
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
};

@Component({
  selector: 'app-inventory', imports: [FormField, CurrencyPipe, DatePipe],
  templateUrl: './inventory.html',
})
export class InventoryComponent {
  api = inject(ApiService);
  section = signal<Section>('panel');
  categories = signal<Category[]>([]);
  products = signal<Product[]>([]);
  allProducts = signal<Product[]>([]);
  movements = signal<Movement[]>([]);
  recentMovements = signal<Movement[]>([]);
  indicators = signal<Indicators>({ productos_activos: 0, productos_stock_bajo: 0, valor_inventario: 0 });
  message = signal(''); error = signal(''); busy = signal(false);
  search = signal(''); categoryFilter = signal('');
  historyProduct = signal(''); from = signal(''); to = signal('');
  editId = signal<number | null>(null);

  categoryModel = signal({ nombre: '', descripcion: '' });
  categoryForm = form(this.categoryModel, s => { required(s.nombre); maxLength(s.nombre, 100); maxLength(s.descripcion, 400); });
  productModel = signal<ProductForm>(emptyProduct());
  productForm = form(this.productModel, s => {
    required(s.codigo); required(s.nombre); required(s.id_categoria);
    maxLength(s.codigo, 40); maxLength(s.nombre, 150); maxLength(s.descripcion, 500);
    min(s.precio_compra, 0.01); min(s.precio_venta, 0.01); min(s.stock_minimo, 0);
  });
  movementModel = signal({ id_producto: '', tipo: 'ENTRADA', cantidad: 1,
    fecha: todayLocal(), motivo: '' });
  movementForm = form(this.movementModel, s => {
    required(s.id_producto); min(s.cantidad, 1); required(s.fecha); required(s.motivo); maxLength(s.motivo, 400);
  });

  constructor() { this.refreshAll(); }

  navigate(section: Section) {
    this.section.set(section); this.message.set(''); this.error.set('');
    if (section === 'stock-bajo' || section === 'productos') this.loadProducts();
    if (section === 'historial' || section === 'movimientos') this.loadMovements();
    if (section === 'panel') this.refreshAll();
  }
  private fail(error: unknown) {
    if (error instanceof HttpErrorResponse && error.status === 401) { this.api.logout(); return; }
    const detail = error instanceof HttpErrorResponse ? error.error?.detail : null;
    this.error.set(typeof detail === 'string' ? detail : 'No se pudo completar la operación.');
    this.busy.set(false);
  }
  refreshAll() {
    this.api.categories().subscribe({ next: data => this.categories.set(data), error: e => this.fail(e) });
    this.api.indicators().subscribe({ next: data => this.indicators.set(data), error: e => this.fail(e) });
    this.loadProducts(); this.loadMovements(); this.loadRecentMovements();
  }
  loadProducts() {
    const lowStock = this.section() === 'stock-bajo';
    this.api.products(lowStock ? '' : this.search(), lowStock ? '' : this.categoryFilter(), lowStock).subscribe({
      next: data => this.products.set(data), error: e => this.fail(e),
    });
    this.api.products().subscribe({ next: data => this.allProducts.set(data), error: e => this.fail(e) });
  }
  loadMovements() {
    this.api.movements(this.historyProduct(), this.from(), this.to()).subscribe({
      next: data => this.movements.set(data), error: e => this.fail(e),
    });
  }
  loadRecentMovements() {
    this.api.movements().subscribe({
      next: data => this.recentMovements.set(data), error: e => this.fail(e),
    });
  }
  saveCategory(event: Event) {
    event.preventDefault(); if (this.categoryForm().invalid()) return;
    this.busy.set(true); this.error.set('');
    this.api.addCategory({ nombre: this.categoryModel().nombre.trim(), descripcion: this.categoryModel().descripcion.trim() })
      .subscribe({ next: () => { this.busy.set(false); this.message.set('Categoría registrada.');
        this.categoryForm().reset({ nombre: '', descripcion: '' }); this.refreshAll(); }, error: e => this.fail(e) });
  }
  saveProduct(event: Event) {
    event.preventDefault(); if (this.productForm().invalid()) return;
    this.busy.set(true); this.error.set('');
    const data = { ...this.productModel(), id_categoria: Number(this.productModel().id_categoria) };
    const request = this.editId() ? this.api.updateProduct(this.editId()!, data) : this.api.addProduct(data);
    request.subscribe({ next: () => { this.busy.set(false); this.message.set(this.editId() ? 'Producto actualizado.' : 'Producto registrado.');
      this.cancelEdit(); this.refreshAll(); }, error: e => this.fail(e) });
  }
  edit(product: Product) {
    this.editId.set(product.id_producto);
    this.productForm().reset({ codigo: product.codigo, nombre: product.nombre, descripcion: product.descripcion,
      id_categoria: String(product.id_categoria), precio_compra: product.precio_compra,
      precio_venta: product.precio_venta, stock_minimo: product.stock_minimo });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  cancelEdit() { this.editId.set(null); this.productForm().reset(emptyProduct()); }
  deactivate(product: Product) {
    if (!confirm(`¿Desactivar ${product.nombre}? Su historial se conservará.`)) return;
    this.api.deactivateProduct(product.id_producto).subscribe({
      next: () => { this.message.set('Producto desactivado.'); this.refreshAll(); }, error: e => this.fail(e),
    });
  }
  saveMovement(event: Event) {
    event.preventDefault(); if (this.movementForm().invalid()) return;
    const data = this.movementModel();
    this.busy.set(true); this.error.set('');
    this.api.addMovement({ ...data, id_producto: Number(data.id_producto), fecha: `${data.fecha}T12:00:00` }).subscribe({
      next: () => { this.busy.set(false); this.message.set('Movimiento registrado y stock actualizado.');
        this.movementForm().reset({ id_producto: '', tipo: 'ENTRADA', cantidad: 1,
          fecha: todayLocal(), motivo: '' }); this.refreshAll(); },
      error: e => this.fail(e),
    });
  }
}
