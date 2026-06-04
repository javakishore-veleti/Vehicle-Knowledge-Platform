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

export interface SearchResponse {
  framework: string;
  store: VectorStore;
  query: string;
  answer: string;
  answerSource: 'llm' | 'extractive' | 'none';
  answers: ProviderAnswer[];
  results: SearchResultItem[];
  count: number;
}

export interface SearchOpts {
  framework?: string;
  store?: VectorStore;
  useLlm?: boolean;
  companyId?: string;
  topK?: number;
  providers?: string[];
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
      providers: opts.providers
    };
    // Attach the encrypted session token (guest) so the backend ties the query to a session.
    return this.session.ensureToken().pipe(switchMap(token => {
      const headers = token ? new HttpHeaders({ 'X-VKP-Session': token }) : undefined;
      return this.http.post<SearchResponse>(`${this.base}/${framework}/search`, body, { headers });
    }));
  }
}
