import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { Category, Indicators, Movement, Product, ProductInput, RegisterInput } from '../Interface/models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private token = sessionStorage.getItem('token') ?? '';
  loggedIn = signal(Boolean(this.token));
  name = signal(sessionStorage.getItem('name') ?? '');

  // /api pasa por el proxy de Angular; las pantallas no necesitan una URL localhost.
  private url = '/api';
  private options() { return { headers: new HttpHeaders({ Authorization: `Bearer ${this.token}` }) }; }

  login(usuario: string, contrasena: string) {
    return this.http.post<{ access_token: string; nombre: string }>(`${this.url}/auth/login`, { usuario, contrasena });
  }
  register(body: RegisterInput) {
    return this.http.post<{ id_usuario: number }>(`${this.url}/auth/register`, body);
  }
  setSession(token: string, name: string) {
    this.token = token; this.name.set(name); this.loggedIn.set(true);
    sessionStorage.setItem('token', token); sessionStorage.setItem('name', name);
  }
  logout() {
    this.token = ''; this.loggedIn.set(false); this.name.set('');
    sessionStorage.removeItem('token'); sessionStorage.removeItem('name');
  }
  categories() { return this.http.get<Category[]>(`${this.url}/categorias`, this.options()); }
  addCategory(body: { nombre: string; descripcion: string }) { return this.http.post<Category>(`${this.url}/categorias`, body, this.options()); }
  products(search = '', category = '', low = false, active = true) {
    let params = new HttpParams().set('solo_bajo', low).set('solo_activos', active);
    if (search) params = params.set('buscar', search);
    if (category) params = params.set('id_categoria', category);
    return this.http.get<Product[]>(`${this.url}/productos`, { ...this.options(), params });
  }
  addProduct(body: ProductInput) { return this.http.post(`${this.url}/productos`, body, this.options()); }
  updateProduct(id: number, body: ProductInput) { return this.http.put(`${this.url}/productos/${id}`, body, this.options()); }
  deactivateProduct(id: number) { return this.http.delete(`${this.url}/productos/${id}`, this.options()); }
  movements(product = '', from = '', to = '') {
    let params = new HttpParams();
    if (product) params = params.set('id_producto', product);
    if (from) params = params.set('desde', `${from}T00:00:00`);
    if (to) params = params.set('hasta', `${to}T23:59:59`);
    return this.http.get<Movement[]>(`${this.url}/movimientos`, { ...this.options(), params });
  }
  addMovement(body: { id_producto: number; tipo: string; cantidad: number; fecha: string; motivo: string }) {
    return this.http.post(`${this.url}/movimientos`, body, this.options());
  }
  indicators() { return this.http.get<Indicators>(`${this.url}/indicadores`, this.options()); }
}
