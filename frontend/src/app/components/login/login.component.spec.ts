import { of, throwError } from 'rxjs';
import { Router } from '@angular/router';

import { AuthService } from '../../auth.service';
import { LoginComponent } from './login.component';

describe('LoginComponent', () => {
  let auth: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  let component: LoginComponent;

  beforeEach(() => {
    auth = jasmine.createSpyObj<AuthService>('AuthService', ['login']);
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    component = new LoginComponent(auth, router);
  });

  it('navigates to search after successful login', () => {
    auth.login.and.returnValue(of(void 0));
    component.email = 'user@example.com';
    component.password = 'password123';

    component.login();

    expect(auth.login).toHaveBeenCalledWith('user@example.com', 'password123');
    expect(router.navigate).toHaveBeenCalledWith(['/search']);
  });

  it('displays error message on failed login', () => {
    auth.login.and.returnValue(throwError(() => new Error('Unauthorized')));
    component.email = 'user@example.com';
    component.password = 'wrong';

    component.login();

    expect(component.error).toBe('Connexion échouée. Vérifiez vos identifiants.');
  });
});
