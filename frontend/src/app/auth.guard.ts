import { inject } from '@angular/core';
import { CanActivateFn, Router, UrlTree } from '@angular/router';

import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = (): boolean | UrlTree => {
  const auth = inject(AuthService);
  const router = inject(Router);

  // Return a UrlTree so Angular cancels the protected navigation cleanly.
  return auth.isLoggedIn() ? true : router.createUrlTree(['/login']);
};
