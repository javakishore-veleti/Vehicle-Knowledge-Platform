import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { CompanyResource } from './models';

interface ListResp { resources: CompanyResource[]; count: number; }
interface OneResp { resource: CompanyResource; }
interface DeleteResp { resourceId: string; deleted: boolean; }

/** Company Resources CRUD via company-service (proxied to :8081), nested under a company. */
@Injectable({ providedIn: 'root' })
export class CompResourceService {
  private base(companyId: string): string {
    return `/admin/company/service/v1/crud/companies/${companyId}/resources`;
  }

  constructor(private http: HttpClient) {}

  list(companyId: string): Observable<CompanyResource[]> {
    return this.http.get<ListResp>(this.base(companyId)).pipe(map(r => r.resources ?? []));
  }

  create(companyId: string, resource: CompanyResource): Observable<CompanyResource> {
    return this.http.post<OneResp>(this.base(companyId), resource).pipe(map(r => r.resource));
  }

  update(companyId: string, resourceId: string, resource: CompanyResource): Observable<CompanyResource> {
    return this.http.put<OneResp>(`${this.base(companyId)}/${resourceId}`, resource).pipe(map(r => r.resource));
  }

  remove(companyId: string, resourceId: string): Observable<DeleteResp> {
    return this.http.delete<DeleteResp>(`${this.base(companyId)}/${resourceId}`);
  }
}
