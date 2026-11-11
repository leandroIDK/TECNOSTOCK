import { Component, inject, signal } from '@angular/core';
import { FormField, form, maxLength, minLength, required } from '@angular/forms/signals';
import { HttpErrorResponse } from '@angular/common/http';
import { ApiService } from '../../service/api.service';

@Component({
  selector: 'app-login', imports: [FormField],
  templateUrl: './login.html',
})
export class LoginComponent {
  private api = inject(ApiService);
  registerMode = signal(false);
  model = signal({ usuario: '', contrasena: '' });
  fields = form(this.model, s => { required(s.usuario); required(s.contrasena); });
  registrationModel = signal({ dni: '', nombre: '', apellido: '', usuario: '', contrasena: '', confirmacion: '' });
  registrationFields = form(this.registrationModel, s => {
    required(s.dni); minLength(s.dni, 8); maxLength(s.dni, 8);
    required(s.nombre); maxLength(s.nombre, 120);
    required(s.apellido); maxLength(s.apellido, 120);
    required(s.usuario); maxLength(s.usuario, 80);
    required(s.contrasena); minLength(s.contrasena, 8);
    required(s.confirmacion);
  });
  error = signal(''); success = signal(''); busy = signal(false);
  showRegistration(value: boolean) {
    this.registerMode.set(value);
    this.error.set(''); this.success.set('');
  }
  submit(event: Event) {
    event.preventDefault();
    if (this.fields().invalid()) return;
    this.busy.set(true); this.error.set('');
    const { usuario, contrasena } = this.model();
    this.api.login(usuario, contrasena).subscribe({
      next: result => { this.busy.set(false); this.api.setSession(result.access_token, result.nombre); },
      error: (response: HttpErrorResponse) => {
        this.busy.set(false);
        this.error.set(response.status === 401 ? 'Usuario o contraseña incorrectos.' :
          response.status === 0 ? 'No se pudo conectar con el servidor. Revisa el backend y el proxy.' :
          response.status === 503 ? 'El servidor necesita revisar su configuración. Ejecuta python check_connection.py en backend.' :
          'El servidor no pudo iniciar sesión. Revisa el error en la terminal del backend.');
      },
    });
  }

  submitRegistration(event: Event) {
    event.preventDefault();
    if (this.registrationFields().invalid()) return;
    const data = this.registrationModel();
    if (!/^[0-9]{8}$/.test(data.dni)) { this.error.set('El DNI debe tener 8 dígitos.'); return; }
    if (data.contrasena !== data.confirmacion) { this.error.set('Las contraseñas no coinciden.'); return; }
    if (new TextEncoder().encode(data.contrasena).length > 72) {
      this.error.set('La contraseña supera el límite de 72 bytes de bcrypt.'); return;
    }
    this.busy.set(true); this.error.set('');
    this.api.register({ dni: data.dni, nombre: data.nombre.trim(), apellido: data.apellido.trim(),
      usuario: data.usuario.trim(), contrasena: data.contrasena }).subscribe({
      next: () => {
        this.busy.set(false);
        this.fields().reset({ usuario: data.usuario.trim(), contrasena: '' });
        this.registrationFields().reset({ dni: '', nombre: '', apellido: '', usuario: '', contrasena: '', confirmacion: '' });
        this.registerMode.set(false);
        this.success.set('Cuenta creada. Inicia sesión con tu usuario y contraseña.');
      },
      error: (response: HttpErrorResponse) => {
        this.busy.set(false);
        this.error.set(response.status === 409 ? 'El usuario o DNI ya está registrado.' :
          response.status === 422 ? 'Revisa los datos y la contraseña.' : 'No se pudo crear la cuenta.');
      },
    });
  }
}
