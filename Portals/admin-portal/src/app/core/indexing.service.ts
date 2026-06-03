import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { ResourceGraphNode } from './models';

export interface IndexWorkflow {
  wfId: string;
  name: string;
  wfType: string;          // AIRFLOW | SPRING_AI
  targetRef: string;
  description?: string;
  status?: string;
}

export interface IndexFormula {
  indexFormulaId: string;
  name: string;
  embeddingProvider: string;
  embeddingModel: string;
  params?: string;
  status?: string;
}

export interface ProviderCredential {
  providerCredentialId: string;
  providerType: string;
  name: string;
  status?: string;
}

export interface IndexLog {
  indexLogId: string;
  companyId: string;
  resourceGraphId?: string;
  wfId: string;
  wfType: string;
  indexFormulaId: string;
  provider?: string;
  embeddingModel?: string;
  indexedTo?: string;
  vectorTarget?: string;
  scope?: string;          // WHOLE | SELECTED
  docCount?: number;
  status: string;          // PENDING | IN_PROGRESS | INDEXED | FAILED | SKIPPED
  version?: string;
  runRef?: string;
  chunks?: number;
  error?: string;
  indexStartDt?: string;
  indexEndDt?: string;
  createdDt?: string;
  updatedDt?: string;
}

export interface TriggerIndexReq {
  wfId: string;
  indexFormulaId: string;
  companyName?: string;
  providerCredentialId?: string;
  docIds?: string[];
  force?: boolean;
  triggeredBy?: string;
}

export interface TriggerIndexResp {
  indexLogId: string;
  wfType: string;
  status: string;
  runRef?: string;
  deduped: boolean;
  message: string;
}

export interface RegisterSnapshotResp { registered: number; skipped: number; total: number; }

/** Indexing control plane (proxied to :8086) + snapshot-doc registration via data-collection (:8084). */
@Injectable({ providedIn: 'root' })
export class IndexingService {
  private readonly base = '/admin/indexing/service/v1';
  private readonly dcBase = '/admin/data-collection/service/v1';

  constructor(private http: HttpClient) {}

  workflows(): Observable<IndexWorkflow[]> { return this.http.get<IndexWorkflow[]>(`${this.base}/workflows`); }

  formulas(): Observable<IndexFormula[]> { return this.http.get<IndexFormula[]>(`${this.base}/formulas`); }

  credentials(): Observable<ProviderCredential[]> { return this.http.get<ProviderCredential[]>(`${this.base}/credentials`); }

  logs(companyId: string): Observable<IndexLog[]> {
    return this.http.get<IndexLog[]>(`${this.base}/companies/${companyId}/index-logs`);
  }

  trigger(companyId: string, req: TriggerIndexReq): Observable<TriggerIndexResp> {
    return this.http.post<TriggerIndexResp>(`${this.base}/companies/${companyId}/index`, req);
  }

  /** Snapshot pages already registered as selectable doc PKs (resource_type SNAPSHOT_PAGE). */
  snapshotDocs(companyId: string): Observable<ResourceGraphNode[]> {
    return this.http.get<{ nodes: ResourceGraphNode[]; count: number }>(
      `${this.dcBase}/companies/${companyId}/resource-graph`
    ).pipe(map(r => (r.nodes ?? []).filter(n => n.resourceType === 'SNAPSHOT_PAGE')));
  }

  /** Register a company's filesystem-snapshot pages as graph rows so they become selectable docs. */
  registerSnapshot(companyId: string, company: string): Observable<RegisterSnapshotResp> {
    return this.http.post<RegisterSnapshotResp>(
      `${this.dcBase}/companies/${companyId}/snapshots/${encodeURIComponent(company)}/register`, {}
    );
  }
}
