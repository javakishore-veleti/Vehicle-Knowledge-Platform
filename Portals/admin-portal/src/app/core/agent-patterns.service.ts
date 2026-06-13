import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface RunResult {
  pattern: string;
  framework: string;
  input: string;
  useCase?: string | null;
  answer?: string;
  critique?: string;
  draft?: string;
  steps?: string[];
  iterations?: number;
  model?: string;
  ok?: boolean;
  error?: string;
  latencyMs?: number;
}

/** Calls the agent-patterns-service (proxied to :8094) — runs any pattern × framework × use case cell live. */
@Injectable({ providedIn: 'root' })
export class AgentPatternsService {
  private readonly base = '/agent-patterns';

  constructor(private http: HttpClient) {}

  run(pattern: string, framework: string, input: string, useCase?: string): Observable<RunResult> {
    const body: Record<string, unknown> = { input };
    if (useCase) { body['useCase'] = useCase; }
    return this.http.post<RunResult>(`${this.base}/${pattern}/${framework}/run`, body);
  }

  /** Lightweight reachability probe for the live/offline badge. */
  patterns(): Observable<unknown> {
    return this.http.get(`${this.base}/patterns`);
  }
}
