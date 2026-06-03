import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { DiscoverResult, ResourceGraphNode } from './models';

interface GraphResp { nodes: ResourceGraphNode[]; count: number; total: number; offset: number; }

export interface GraphPage { nodes: ResourceGraphNode[]; total: number; offset: number; }

/** Talks to data-collection-service (proxied to :8084). */
@Injectable({ providedIn: 'root' })
export class DiscoveryService {
  private readonly base = '/admin/data-collection/service/v1';

  constructor(private http: HttpClient) {}

  getGraph(companyId: string): Observable<ResourceGraphNode[]> {
    return this.http.get<GraphResp>(`${this.base}/companies/${companyId}/resource-graph`).pipe(map(r => r.nodes ?? []));
  }

  /** Server-side paged graph (for large 100k+ graphs). */
  getGraphPaged(companyId: string, offset: number, limit: number): Observable<GraphPage> {
    return this.http.get<GraphResp>(`${this.base}/companies/${companyId}/resource-graph`, {
      params: { offset, limit }
    }).pipe(map(r => ({ nodes: r.nodes ?? [], total: r.total ?? 0, offset: r.offset ?? offset })));
  }

  discover(companyId: string, resourceId: string, seedUrl: string): Observable<DiscoverResult> {
    return this.http.post<DiscoverResult>(
      `${this.base}/companies/${companyId}/resources/${resourceId}/discover`,
      { seedUrl, triggeredBy: 'admin-portal' }
    );
  }
}
