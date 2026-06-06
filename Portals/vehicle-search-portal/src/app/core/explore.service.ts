import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { SessionService } from './session.service';

export interface SearchResultItem {
  sourceUrl: string;
  snippet: string;
  score: number;
}

export type VectorStore = 'pgvector' | 'mongodb';

export interface ProviderAnswer {
  provider: string;
  label: string;
  model: string;
  answer: string | null;
  ok: boolean;
  error: string | null;
  errorDetail?: string | null;
  promptTokens?: number | null;
  completionTokens?: number | null;
  totalTokens?: number | null;
  finishReason?: string | null;
  costUsd?: number | null;
  latencyMs: number;
}

export interface ProviderInfo {
  id: string;
  label: string;
  model: string;
  free: boolean;
  default: boolean;
}

export interface FlowStep {
  n: number;
  key: string;
  label: string;
  type: 'request' | 'guardrail' | 'embed' | 'retrieve' | 'llm' | 'store' | 'answer' | string;
  status: 'ok' | 'blocked' | 'error' | 'skip' | string;
  ms?: number | null;
  detail?: Record<string, any>;
}

export interface SearchResponse {
  framework: string;
  store: VectorStore;
  query: string;
  queryId?: string;
  sessionId?: string;
  answer: string;
  answerSource: 'llm' | 'extractive' | 'none';
  answers: ProviderAnswer[];
  results: SearchResultItem[];
  count: number;
  latencyMs?: number;
  logId?: string;
  steps?: FlowStep[];
  techStack?: { layer: string; tech: string }[];
  vendors?: { name: string; kind: string; role?: string; ok?: boolean }[];
}

export interface SearchOpts {
  framework?: string;
  store?: VectorStore;
  useLlm?: boolean;
  companyId?: string;
  topK?: number;
  providers?: string[];
  includeDiagram?: boolean;
  origin?: Record<string, any>;
}

export interface LogListItem {
  id: string;
  created_dt: string;
  title: string;
  query: string;
  store: string;
  mode: string;
  framework: string;
  origin_source: string;
  llm_enabled: boolean;
  status: string;
  latency_ms: number;
  result_count: number;
  vendors?: { name: string }[];
}

export interface LogList {
  mode: 'server' | 'client';
  items: LogListItem[];
  count: number;
  page?: number;
  size?: number;
  total?: number;
  totalPages?: number;
  limit?: number;
}

export interface LogDetail extends LogListItem {
  description: string;
  session_id: string;
  user_type: string;
  request_params: Record<string, any>;
  request_origin: Record<string, any>;
  tech_stack: { layer: string; tech: string }[];
  db_tables: { name: string; db: string; role: string; op: string }[];
  indexes: { name: string; table: string; type: string; used: boolean }[];
  llms: Record<string, any>[];
  vendors: { name: string; kind: string; role?: string; ok?: boolean }[];
  guardrails: Record<string, any>;
  steps: FlowStep[];
  result_summary: Record<string, any>;
  answer: Record<string, any>;
}

/** Talks to vehicle-explore-service (proxied to :8090). Framework is part of the URL. */
@Injectable({ providedIn: 'root' })
export class ExploreService {
  private readonly base = '/api/vehicle-explore';

  constructor(private http: HttpClient, private session: SessionService) {}

  providers(): Observable<ProviderInfo[]> {
    return this.http.get<{ providers: ProviderInfo[] }>(`${this.base}/providers`).pipe(map(r => r.providers ?? []));
  }

  search(query: string, opts: SearchOpts = {}): Observable<SearchResponse> {
    const framework = opts.framework ?? 'langgraph';
    const body = {
      query,
      store: opts.store ?? 'pgvector',
      useLlm: opts.useLlm ?? true,
      companyId: opts.companyId,
      topK: opts.topK ?? 8,
      providers: opts.providers,
      includeDiagram: opts.includeDiagram ?? false,
      origin: opts.origin
    };
    // Attach the encrypted session token (guest) so the backend ties the query to a session.
    return this.session.ensureToken().pipe(switchMap(token => {
      const headers = token ? new HttpHeaders({ 'X-VKP-Session': token }) : undefined;
      return this.http.post<SearchResponse>(`${this.base}/${framework}/search`, body, { headers });
    }));
  }

  /** 👍/👎 on an answer — recorded in search_feedback (a core quality KPI). */
  feedback(rating: 'up' | 'down', queryId?: string, sessionId?: string, provider?: string): Observable<unknown> {
    return this.http.post('/guardrails/v1/feedback', { rating, queryId, sessionId, provider, userType: 'GUEST' });
  }

  /** Search telemetry rows. Server-side page (page/size) or latest-N (limit) for client-side paging. */
  logs(opts: { page?: number; size?: number; limit?: number; store?: string; framework?: string; status?: string } = {}): Observable<LogList> {
    const p = new URLSearchParams();
    if (opts.limit != null) { p.set('limit', String(opts.limit)); }
    else { p.set('page', String(opts.page ?? 0)); p.set('size', String(opts.size ?? 20)); }
    if (opts.store) { p.set('store', opts.store); }
    if (opts.framework) { p.set('framework', opts.framework); }
    if (opts.status) { p.set('status', opts.status); }
    return this.http.get<LogList>(`${this.base}/logs?${p.toString()}`);
  }

  logDetail(id: string): Observable<LogDetail> {
    return this.http.get<LogDetail>(`${this.base}/logs/${id}`);
  }
}
