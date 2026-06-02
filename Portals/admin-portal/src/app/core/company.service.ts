import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { Company } from './models';

interface CompanyResp { company: Company; }
interface CompanyListResp { companies: Company[]; count: number; }
interface DeleteResp { companyId: string; deleted: boolean; }

/** Talks to company-service (proxied to :8081 in dev). */
@Injectable({ providedIn: 'root' })
export class CompanyService {
  private readonly base = '/admin/company/service/v1/crud/companies';

  constructor(private http: HttpClient) {}

  list(): Observable<Company[]> {
    return this.http.get<CompanyListResp>(this.base).pipe(map(r => r.companies ?? []));
  }

  create(company: Company): Observable<Company> {
    return this.http.post<CompanyResp>(this.base, company).pipe(map(r => r.company));
  }

  update(id: string, company: Company): Observable<Company> {
    return this.http.put<CompanyResp>(`${this.base}/${id}`, company).pipe(map(r => r.company));
  }

  remove(id: string): Observable<DeleteResp> {
    return this.http.delete<DeleteResp>(`${this.base}/${id}`);
  }
}
