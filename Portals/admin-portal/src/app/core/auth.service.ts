import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map, shareReplay } from 'rxjs/operators';

interface SigninResp { token: string; tokenType: string; userId: string; email: string; }

/**
 * Obtains and caches an ADMIN bearer JWT. The auth interceptor attaches it to /admin/** calls,
 * which vkp-jwt-rbac now requires (role ADMIN). For localhost dev this auto-signs-in as the
 * seeded admin (matches user-service AdminSeeder defaults); a login form can replace this later.
 * If user-service is down it returns '' and the call proceeds tokenless (and will get a 401).
 */
@Injectable({ providedIn: 'root' })
export class AuthService {
  private token = '';
  private token$?: Observable<string>;

  constructor(private http: HttpClient) {}

  ensureToken(): Observable<string> {
    if (this.token) { return of(this.token); }
    if (!this.token$) {
      this.token$ = this.http.post<SigninResp>('/customer/user/service/v1/auth/signin',
        { email: 'admin@vkp.local', password: 'admin12345' }).pipe(
        map(r => { this.token = r.token ?? ''; return this.token; }),
        catchError(() => of('')),
        shareReplay(1)
      );
    }
    return this.token$;
  }
}
