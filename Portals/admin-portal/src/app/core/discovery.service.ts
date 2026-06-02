import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { DiscoverResult, ResourceGraphNode } from './models';

interface GraphResp { nodes: ResourceGraphNode[]; count: number; }

/** Talks to data-collection-service (proxied to :8084). */
@Injectable({ providedIn: 'root' })
export class DiscoveryService {
  private readonly base = '/admin/data-collection/service/v1';

  constructor(private http: HttpClient) {}

  getGraph(companyId: string): Observable<ResourceGraphNode[]> {
    return this.http.get<GraphResp>(`${this.base}/companies/${companyId}/resource-graph`).pipe(map(r => r.nodes ?? []));
  }

  discover(companyId: string, resourceId: string, seedUrl: string): Observable<DiscoverResult> {
    return this.http.post<DiscoverResult>(
      `${this.base}/companies/${companyId}/resources/${resourceId}/discover`,
      { seedUrl, triggeredBy: 'admin-portal' }
    );
  }
}
