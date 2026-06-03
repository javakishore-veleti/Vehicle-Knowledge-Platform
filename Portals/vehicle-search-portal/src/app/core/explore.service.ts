import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface SearchResultItem {
  sourceUrl: string;
  snippet: string;
  score: number;
}

export interface SearchResponse {
  framework: string;
  query: string;
  answer: string;
  results: SearchResultItem[];
  count: number;
}

/** Talks to vehicle-explore-service (proxied to :8090). Framework is part of the URL. */
@Injectable({ providedIn: 'root' })
export class ExploreService {
  private readonly base = '/api/vehicle-explore';

  constructor(private http: HttpClient) {}

  search(query: string, framework = 'langgraph', companyId?: string, topK = 5): Observable<SearchResponse> {
    return this.http.post<SearchResponse>(`${this.base}/${framework}/search`, { query, companyId, topK });
  }
}
