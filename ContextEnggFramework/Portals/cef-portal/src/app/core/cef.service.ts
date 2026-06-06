import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface FlowStep {
  n: number; key: string; label: string; type: string; status: string;
  ms?: number | null; desc?: string; detail?: Record<string, any>;
}

export interface OrchestrateResult {
  answer: string; model: string;
  context: { retrieved: number; used: number; memoryTurns: number; strategies: string[] };
  sources: { n: number; sourceUrl: string; score: number }[];
  latencyMs: number;
  logId?: string;
  steps?: FlowStep[];
  techStack?: { layer: string; tech: string }[];
  vendors?: { name: string; kind: string; role?: string; ok?: boolean; description?: string }[];
}

export interface Strategy {
  id: string; name: string; description: string; charBudget: number; status: string;
  selectionEnabled: boolean; compressionEnabled: boolean; orderingEnabled: boolean;
  isolationEnabled: boolean; formatEnabled: boolean;
}

export interface CefLogItem {
  id: string; created_dt: string; title: string; query: string; knowledge_base: string;
  role: string; model: string; framework: string; origin_source: string; status: string;
  latency_ms: number; retrieved: number; used: number; memory_turns: number;
  vendors?: { name: string }[];
}

export interface CefLogList {
  mode: 'server' | 'client'; items: CefLogItem[]; count: number;
  page?: number; size?: number; total?: number; totalPages?: number; limit?: number;
}

export interface CefLogDetail extends CefLogItem {
  description: string; company_id: string; session_id: string;
  request_params: Record<string, any>; request_origin: Record<string, any>;
  scope: Record<string, any>; strategies: Record<string, any>[];
  tech_stack: { layer: string; tech: string }[];
  db_tables: { name: string; db: string; role: string; op: string }[];
  indexes: { name: string; table: string; type: string; used: boolean }[];
  llms: Record<string, any>[];
  vendors: { name: string; kind: string; role?: string; ok?: boolean; description?: string }[];
  steps: FlowStep[]; result_summary: Record<string, any>; answer: Record<string, any>;
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

  /** CEF chat telemetry rows. Server-side (page/size) or latest-N (limit) for client-side paging. */
  logs(opts: { page?: number; size?: number; limit?: number; companyId?: string; status?: string } = {}): Observable<CefLogList> {
    const p = new URLSearchParams();
    if (opts.limit != null) { p.set('limit', String(opts.limit)); }
    else { p.set('page', String(opts.page ?? 0)); p.set('size', String(opts.size ?? 20)); }
    if (opts.companyId) { p.set('companyId', opts.companyId); }
    if (opts.status) { p.set('status', opts.status); }
    return this.http.get<CefLogList>(`/context-engine/logs?${p.toString()}`);
  }

  logDetail(id: string): Observable<CefLogDetail> {
    return this.http.get<CefLogDetail>(`/context-engine/logs/${id}`);
  }
}
