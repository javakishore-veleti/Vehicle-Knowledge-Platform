import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface OrchestrateResult {
  answer: string; model: string;
  context: { retrieved: number; used: number; memoryTurns: number; strategies: string[] };
  sources: { n: number; sourceUrl: string; score: number }[];
  latencyMs: number;
}

export interface Strategy {
  id: string; name: string; description: string; charBudget: number; status: string;
  selectionEnabled: boolean; compressionEnabled: boolean; orderingEnabled: boolean;
  isolationEnabled: boolean; formatEnabled: boolean;
}

/** Talks to the CEF services: the context-engine orchestrator (:8093, proxied /context-engine)
 *  and context-admin (:8094, proxied /admin/context-engine). */
@Injectable({ providedIn: 'root' })
export class CefService {
  private readonly admin = '/admin/context-engine/service/v1';
  constructor(private http: HttpClient) {}

  orchestrate(body: Record<string, unknown>): Observable<OrchestrateResult> {
    return this.http.post<OrchestrateResult>('/context-engine/orchestrate', body);
  }
  strategies(): Observable<Strategy[]> {
    return this.http.get<Strategy[]>(`${this.admin}/crud/strategies`);
  }
  evalRun(body: Record<string, unknown>): Observable<any> {
    return this.http.post(`${this.admin}/eval/run`, body);
  }
}
