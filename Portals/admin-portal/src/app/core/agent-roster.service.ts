import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Roster {
  services: { explore: string; agentic: string; agenticReachable: boolean };
  matrix: Record<string, string[]>;                                   // stage -> [frameworks]
  byFramework: Record<string, { service: string; stages: string[] }>; // framework -> {service, stages}
  frameworkCount: number;
}

/**
 * The unified agent-framework roster. Reads /api/vehicle-explore/roster (explore :8090, which also
 * aggregates the agentic-service :8092), and runs a stage against a framework — routing to the
 * explore endpoints for the classic frameworks or the agentic-service for the new SDKs.
 */
@Injectable({ providedIn: 'root' })
export class AgentRosterService {
  constructor(private http: HttpClient) {}

  roster(): Observable<Roster> {
    return this.http.get<Roster>('/api/vehicle-explore/roster');
  }

  run(stage: string, framework: string, service: string, body: Record<string, unknown>): Observable<unknown> {
    return service === 'agentic'
      ? this.http.post(`/agentic/${stage}/${framework}/run`, body)
      : this.http.post(`/api/vehicle-explore/${framework}/${stage}`, body);
  }
}
