import { Component } from '@angular/core';
import { Router } from '@angular/router';

import { AuthService } from '../../auth.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['../../app.component.css'],
})
export class RegisterComponent {
  name = '';
  email = '';
  password = '';
  error = '';

  constructor(private readonly auth: AuthService, private readonly router: Router) {}

  register(): void {
    this.error = '';
    if (this.password.length < 8) {
      this.error = 'Le mot de passe doit contenir au moins 8 caracteres.';
      return;
    }

    this.auth.register({ name: this.name, email: this.email, password: this.password }).subscribe({
      next: () => {
        // Registration does not auto-login; redirecting keeps token creation in one flow.
        this.router.navigate(['/login']);
      },
      error: (response) => {
        const detail = response?.error?.detail;
        if (detail === 'Email deja utilise') {
          this.error = 'Cet email est deja utilise. Connectez-vous ou choisissez une autre adresse.';
          return;
        }

        this.error = 'Inscription echouee. Verifiez que le nom, l email et le mot de passe sont valides.';
      },
    });
  }
}
