import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface CrawlTriggerResult {
  dagId: string;
  dagRunId: string;
  state: string;
}

/** Triggers the filesystem-snapshot crawl via data-collection-service (proxied to :8084). */
@Injectable({ providedIn: 'root' })
export class CrawlService {
  private readonly base = '/admin/data-collection/service/v1';

  constructor(private http: HttpClient) {}

  trigger(companyId: string, maxPages: number, maxDepth: number): Observable<CrawlTriggerResult> {
    return this.http.post<CrawlTriggerResult>(
      `${this.base}/companies/${companyId}/crawl`,
      { maxPages, maxDepth, triggeredBy: 'admin-portal' }
    );
  }
}
