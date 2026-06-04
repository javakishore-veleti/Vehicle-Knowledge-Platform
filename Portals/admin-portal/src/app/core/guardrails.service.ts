import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

export interface QueryLogRow {
  queryId: string;
  sessionId: string;
  userType: 'GUEST' | 'AUTH';
  userId?: string | null;
  queryText: string;
  inputAction?: string | null;
  outputAction?: string | null;
  createdDt: string;
}

/** Reads the guardrails query ledger (proxied to :8091). */
@Injectable({ providedIn: 'root' })
export class GuardrailsService {
  private readonly base = '/guardrails/v1';

  constructor(private http: HttpClient) {}

  recentQueries(userType = '', limit = 100): Observable<QueryLogRow[]> {
    const params: Record<string, string> = { limit: String(limit) };
    if (userType) { params['userType'] = userType; }
    return this.http.get<{ queries: QueryLogRow[] }>(`${this.base}/admin/queries`, { params })
      .pipe(map(r => r.queries ?? []));
  }
}
