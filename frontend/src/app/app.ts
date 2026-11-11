import { Component, inject } from '@angular/core';
import { ApiService } from './api.service';
import { LoginComponent } from './login';
import { InventoryComponent } from './inventory';

@Component({
  imports: [LoginComponent, InventoryComponent],
  selector: 'app-root',
  template: `@if (api.loggedIn()) { <app-inventory /> } @else { <app-login /> }`,
})
export class App {
  api = inject(ApiService);
}
