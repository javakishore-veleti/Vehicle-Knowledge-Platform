import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface SearchResultItem {
  sourceUrl: string;
  snippet: string;
  score: number;
}

export type VectorStore = 'pgvector' | 'mongodb';

export interface SearchResponse {
  framework: string;
  store: VectorStore;
  query: string;
  answer: string;
  answerSource: 'llm' | 'extractive' | 'none';
  results: SearchResultItem[];
  count: number;
}

export interface SearchOpts {
  framework?: string;
  store?: VectorStore;
  useLlm?: boolean;
  companyId?: string;
  topK?: number;
}

/** Talks to vehicle-explore-service (proxied to :8090). Framework is part of the URL. */
@Injectable({ providedIn: 'root' })
export class ExploreService {
  private readonly base = '/api/vehicle-explore';

  constructor(private http: HttpClient) {}

  search(query: string, opts: SearchOpts = {}): Observable<SearchResponse> {
    const framework = opts.framework ?? 'langgraph';
    return this.http.post<SearchResponse>(`${this.base}/${framework}/search`, {
      query,
      store: opts.store ?? 'pgvector',
      useLlm: opts.useLlm ?? true,
      companyId: opts.companyId,
      topK: opts.topK ?? 6
    });
  }
}
