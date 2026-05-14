import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

import { ApiService } from './api.service';

describe('ApiService', () => {
  let service: ApiService;
  let http: HttpTestingController;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
    });
    service = TestBed.inject(ApiService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    http.verify();
    localStorage.clear();
  });

  it('uses the gateway API prefix', () => {
    expect(service.apiBase).toBe('/api/v1');
  });

  it('adds the bearer token when one is stored', () => {
    localStorage.setItem('auth_token', 'token-123');

    service.get<{ ok: boolean }>('/dashboard/').subscribe(response => {
      expect(response.ok).toBeTrue();
    });

    const request = http.expectOne('/api/v1/dashboard/');
    expect(request.request.headers.get('Authorization')).toBe('Bearer token-123');
    request.flush({ ok: true });
  });

  it('keeps anonymous requests without an authorization header', () => {
    service.post<{ id: number }>('/auth/register', { email: 'reader@example.com' }).subscribe(response => {
      expect(response.id).toBe(1);
    });

    const request = http.expectOne('/api/v1/auth/register');
    expect(request.request.headers.has('Authorization')).toBeFalse();
    request.flush({ id: 1 });
  });
});
