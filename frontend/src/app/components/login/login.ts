import { Component, inject, signal } from '@angular/core';
import { FormField, form, required } from '@angular/forms/signals';
import { ApiService } from '../../service/api.service';

@Component({
  selector: 'app-login', imports: [FormField],
  template: `<main class="login-page"><form class="login-card" (submit)="submit($event)">
    <span class="eyebrow">TECNOSTOCK</span><h1>Control de inventario</h1>
    <p>Ingresa para administrar productos y movimientos.</p>
    <label>Usuario<input [formField]="fields.usuario" autocomplete="username"></label>
    @if (fields.usuario().touched() && fields.usuario().invalid()) { <small>Ingresa tu usuario.</small> }
    <label>Contraseña<input type="password" [formField]="fields.contrasena" autocomplete="current-password"></label>
    @if (fields.contrasena().touched() && fields.contrasena().invalid()) { <small>Ingresa tu contraseña.</small> }
    @if (error()) { <div class="error">{{ error() }}</div> }
    <button [disabled]="fields().invalid() || busy()">{{ busy() ? 'Ingresando…' : 'Ingresar' }}</button>
  </form></main>`,
})
export class LoginComponent {
  private api = inject(ApiService);
  model = signal({ usuario: '', contrasena: '' });
  fields = form(this.model, s => { required(s.usuario); required(s.contrasena); });
  error = signal(''); busy = signal(false);
  submit(event: Event) {
    event.preventDefault();
    if (this.fields().invalid()) return;
    this.busy.set(true); this.error.set('');
    const { usuario, contrasena } = this.model();
    this.api.login(usuario, contrasena).subscribe({
      next: result => { this.busy.set(false); this.api.setSession(result.access_token, result.nombre); },
      error: () => { this.busy.set(false); this.error.set('No se pudo iniciar sesión. Revisa tus credenciales.'); },
    });
  }
}
