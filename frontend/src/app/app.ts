import { Component, inject } from '@angular/core';
import { ApiService } from './service/api.service';
import { LoginComponent } from './components/login/login';
import { InventoryComponent } from './components/inventory/inventory';

@Component({
  imports: [LoginComponent, InventoryComponent],
  selector: 'app-root',
  template: `@if (api.loggedIn()) { <app-inventory /> } @else { <app-login /> }`,
})
export class App {
  api = inject(ApiService);
}
