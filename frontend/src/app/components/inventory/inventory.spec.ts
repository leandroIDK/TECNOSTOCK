import { TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';
import { of } from 'rxjs';
import { expect, it, vi } from 'vitest';

import { ApiService } from '../../service/api.service';
import { InventoryComponent } from './inventory';

function setup() {
  const api = {
    name: signal('Prueba'),
    logout: vi.fn(),
    categories: vi.fn(() => of([])),
    indicators: vi.fn(() => of({ productos_activos: 0, productos_stock_bajo: 0, valor_inventario: 0 })),
    products: vi.fn(() => of([])),
    movements: vi.fn(() => of([])),
  };
  TestBed.configureTestingModule({ imports: [InventoryComponent], providers: [{ provide: ApiService, useValue: api }] });
  const component = TestBed.createComponent(InventoryComponent).componentInstance;
  return { component, api };
}

it('stock bajo ignora la búsqueda usada en productos', () => {
  const { component, api } = setup();
  component.search.set('SSD');
  component.categoryFilter.set('2');
  api.products.mockClear();
  component.navigate('stock-bajo');
  expect(api.products).toHaveBeenCalledWith('', '', true);
});

it('el panel consulta movimientos recientes sin filtros del historial', () => {
  const { component, api } = setup();
  component.historyProduct.set('2');
  component.from.set('2026-01-01');
  component.to.set('2026-01-31');
  component.navigate('historial');
  api.movements.mockClear();
  component.navigate('panel');
  expect(api.movements).toHaveBeenCalledWith();
});
