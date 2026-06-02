import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { WorkflowRun } from './models';

interface WorkflowListResp { runs: WorkflowRun[]; count: number; }

/** Talks to data-collection-service (proxied to :8084), which proxies to airflow-adapter-service. */
@Injectable({ providedIn: 'root' })
export class WorkflowService {
  private readonly base = '/admin/data-collection/service/v1/workflows';

  constructor(private http: HttpClient) {}

  list(dagId: string): Observable<WorkflowRun[]> {
    return this.http.get<WorkflowListResp>(`${this.base}/${dagId}`).pipe(map(r => r.runs ?? []));
  }
}
