import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

export interface SnapshotCompany {
  company: string;
  completed: boolean;
  pages: number;
  files: number;
  images: number;
  completedAt?: string;
}

export interface SnapshotImageRef { imageId: string; src: string; file: string; }

export interface SnapshotPage {
  url: string;
  depth: number;
  title?: string;
  text?: string;
  textLength: number;
  images: SnapshotImageRef[];
  linksCount: number;
  fetchedAt?: string;
}

export interface SnapshotPages {
  company: string;
  pages: SnapshotPage[];
  count: number;
  total: number;
  offset: number;
}

/** Browses crawl snapshots via data-collection-service (proxied to :8084). */
@Injectable({ providedIn: 'root' })
export class SnapshotService {
  private readonly base = '/admin/data-collection/service/v1/snapshots';

  constructor(private http: HttpClient) {}

  listCompanies(): Observable<SnapshotCompany[]> {
    return this.http.get<{ companies: SnapshotCompany[]; count: number }>(this.base).pipe(map(r => r.companies ?? []));
  }

  pages(company: string, offset: number, limit: number): Observable<SnapshotPages> {
    return this.http.get<SnapshotPages>(`${this.base}/${encodeURIComponent(company)}/pages`, {
      params: { offset, limit }
    });
  }

  imageUrl(company: string, imageId: string): string {
    return `${this.base}/${encodeURIComponent(company)}/images/${imageId}`;
  }
}
