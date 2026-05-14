import { of, throwError } from 'rxjs';
import { Router } from '@angular/router';

import { AuthService } from '../../auth.service';
import { RegisterComponent } from './register.component';

describe('RegisterComponent', () => {
  let auth: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  let component: RegisterComponent;

  beforeEach(() => {
    auth = jasmine.createSpyObj<AuthService>('AuthService', ['register']);
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    component = new RegisterComponent(auth, router);
  });

  it('rejects passwords shorter than eight characters before calling the API', () => {
    component.password = 'short';

    component.register();

    expect(component.error).toBe('Le mot de passe doit contenir au moins 8 caracteres.');
    expect(auth.register).not.toHaveBeenCalled();
  });

  it('redirects to login after a successful registration', () => {
    auth.register.and.returnValue(of({ id: 1, name: 'Reader', email: 'reader@example.com' }));
    component.name = 'Reader';
    component.email = 'reader@example.com';
    component.password = 'password123';

    component.register();

    expect(auth.register).toHaveBeenCalledWith({
      name: 'Reader',
      email: 'reader@example.com',
      password: 'password123',
    });
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('shows a specific message when the email is already used', () => {
    auth.register.and.returnValue(throwError(() => ({ error: { detail: 'Email deja utilise' } })));
    component.password = 'password123';

    component.register();

    expect(component.error).toBe('Cet email est deja utilise. Connectez-vous ou choisissez une autre adresse.');
  });

  it('shows a helpful fallback message for invalid registration data', () => {
    auth.register.and.returnValue(throwError(() => ({ error: { detail: 'invalid payload' } })));
    component.password = 'password123';

    component.register();

    expect(component.error).toBe('Inscription echouee. Verifiez que le nom, l email et le mot de passe sont valides.');
  });
});
