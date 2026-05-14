import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

import { ApiService } from './services/api.service';
import { User } from './models';

interface TokenResponse {
  access_token: string;
  token_type: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  constructor(private readonly api: ApiService, private readonly http: HttpClient) {}

  login(email: string, password: string): Observable<TokenResponse> {
    // FastAPI's OAuth2PasswordRequestForm expects form-encoded credentials, not JSON.
    const body = new HttpParams()
      .set('username', email)
      .set('password', password)
      .set('grant_type', 'password');

    return this.http.post<TokenResponse>(`${this.api.apiBase}/auth/token`, body.toString(), {
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    }).pipe(
      tap(token => {
        // Keep the token client-side so refreshes do not force a new login during demos.
        localStorage.setItem('auth_token', token.access_token);
      })
    );
  }

  register(user: { name: string; email: string; password: string }): Observable<User> {
    return this.api.post<User>('/auth/register', user);
  }

  logout(): void {
    // Removing the token is enough because the backend validates stateless JWTs.
    localStorage.removeItem('auth_token');
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('auth_token');
  }
}
