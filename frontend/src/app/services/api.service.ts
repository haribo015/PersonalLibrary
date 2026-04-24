import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  public apiBase = globalThis.location.port === '4200' ? 'http://localhost:8000/api/v1' : '/api/v1';

  constructor(private readonly http: HttpClient) {}

  private getAuthHeaders(): HttpHeaders | undefined {
    const token = localStorage.getItem('auth_token');
    return token ? new HttpHeaders({ Authorization: `Bearer ${token}` }) : undefined;
  }

  get<T>(path: string): Observable<T> {
    return this.http.get<T>(`${this.apiBase}${path}`, {
      headers: this.getAuthHeaders(),
    });
  }

  post<T>(path: string, payload: unknown): Observable<T> {
    return this.http.post<T>(`${this.apiBase}${path}`, payload, {
      headers: this.getAuthHeaders(),
    });
  }

  delete<T>(path: string): Observable<T> {
    return this.http.delete<T>(`${this.apiBase}${path}`, {
      headers: this.getAuthHeaders(),
    });
  }

  patch<T>(path: string, payload: unknown): Observable<T> {
    return this.http.patch<T>(`${this.apiBase}${path}`, payload, {
      headers: this.getAuthHeaders(),
    });
  }
}
