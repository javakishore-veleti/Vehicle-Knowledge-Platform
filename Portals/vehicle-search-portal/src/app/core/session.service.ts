import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map, shareReplay } from 'rxjs/operators';

interface SessionResp { sessionId: string; userType: string; token: string; }

/**
 * Fetches a guest session token from user-service once and caches it. The token is the encrypted
 * X-VKP-Session value sent on every search. If user-service is down, returns '' (the explore
 * service falls back to a fresh guest session, so search still works).
 */
@Injectable({ providedIn: 'root' })
export class SessionService {
  private token = '';
  private token$?: Observable<string>;

  constructor(private http: HttpClient) {}

  ensureToken(): Observable<string> {
    if (this.token) { return of(this.token); }
    if (!this.token$) {
      this.token$ = this.http.post<SessionResp>('/customer/user/service/v1/session/guest', {}).pipe(
        map(r => { this.token = r.token ?? ''; return this.token; }),
        catchError(() => of('')),
        shareReplay(1)
      );
    }
    return this.token$;
  }
}
