import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TableModule, TableLazyLoadEvent } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { SnapshotCompany, SnapshotPage, SnapshotService } from '../../core/snapshot.service';

@Component({
  selector: 'vkp-snapshots',
  standalone: true,
  imports: [CommonModule, FormsModule, TableModule, ButtonModule, TagModule],
  template: `
  <h1 class="vkp-page-title">Data Collection <span class="vkp-muted">› Snapshot Browser</span></h1>

  <div class="vkp-card" style="margin-bottom:1.25rem;">
    <div class="vkp-toolbar">
      <label style="font-weight:600;">Company snapshot</label>
      <select [(ngModel)]="company" (ngModelChange)="onCompanyChange()"
              style="padding:.5rem;border:1px solid var(--vkp-border);border-radius:6px;min-width:240px;">
        <option *ngFor="let c of companies" [value]="c.company">{{ c.company }} ({{ c.pages }} pages)</option>
      </select>
      <span *ngIf="selected()" class="vkp-muted">
        <p-tag [value]="selected()!.completed ? 'completed' : 'in progress'" [severity]="selected()!.completed ? 'success' : 'info'"></p-tag>
        &nbsp;{{ selected()!.pages }} pages · {{ selected()!.images }} images · {{ selected()!.files }} file(s)
      </span>
      <span class="vkp-spacer"></span>
      <p-button label="Refresh" icon="pi pi-refresh" [outlined]="true" (onClick)="reload()"></p-button>
    </div>
    <div *ngIf="error" style="background:#fde8e8;color:#9b1c1c;border:1px solid #f8b4b4;padding:.6rem .9rem;border-radius:6px;">{{ error }}</div>
    <p *ngIf="!companies.length && !error" class="vkp-muted" style="margin:.25rem 0 0;">No snapshots yet — trigger a crawl from <b>Crawl Snapshot</b>.</p>
  </div>

  <div class="vkp-card" *ngIf="company">
    <p-table [value]="pages" dataKey="url" [lazy]="true" (onLazyLoad)="load($event)"
             [paginator]="true" [rows]="rows" [first]="first" [totalRecords]="total" [loading]="loading"
             [rowsPerPageOptions]="[10,25,50]" [tableStyle]="{ 'min-width': '52rem' }"
             currentPageReportTemplate="{first}–{last} of {totalRecords}" [showCurrentPageReport]="true">
      <ng-template pTemplate="header">
        <tr>
          <th style="width:3rem"></th>
          <th style="width:4rem">Depth</th>
          <th>Title / URL</th>
          <th style="width:6rem">Images</th>
          <th style="width:6rem">Text</th>
        </tr>
      </ng-template>
      <ng-template pTemplate="body" let-p let-expanded="expanded">
        <tr>
          <td>
            <button type="button" [pRowToggler]="p" style="background:none;border:none;cursor:pointer;color:var(--vkp-muted);">
              <i class="pi" [ngClass]="expanded ? 'pi-chevron-down' : 'pi-chevron-right'"></i>
            </button>
          </td>
          <td><p-tag [value]="'d' + p.depth" severity="secondary"></p-tag></td>
          <td>
            <div style="font-weight:600;">{{ p.title || '(untitled)' }}</div>
            <a [href]="p.url" target="_blank" rel="noopener" style="color:var(--vkp-brand-2);font-size:.85rem;">{{ p.url }}</a>
          </td>
          <td>{{ p.images.length }}</td>
          <td>{{ p.textLength | number }}</td>
        </tr>
      </ng-template>
      <ng-template pTemplate="rowexpansion" let-p>
        <tr>
          <td colspan="5">
            <div style="padding:.5rem 0 1rem;">
              <div *ngIf="p.images.length" style="display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:.75rem;">
                <img *ngFor="let img of p.images" [src]="imgUrl(img.imageId)" [alt]="img.src"
                     loading="lazy" style="height:90px;border:1px solid var(--vkp-border);border-radius:6px;object-fit:cover;background:#fafafa;" />
              </div>
              <div class="vkp-muted" style="white-space:pre-wrap;font-size:.85rem;max-height:240px;overflow:auto;">{{ p.text }}<span *ngIf="p.textLength > (p.text?.length || 0)"> …(truncated, {{ p.textLength | number }} chars total)</span></div>
            </div>
          </td>
        </tr>
      </ng-template>
      <ng-template pTemplate="emptymessage">
        <tr><td colspan="5" class="vkp-muted" style="text-align:center;padding:1.5rem;">No pages in this snapshot.</td></tr>
      </ng-template>
    </p-table>
  </div>
  `
})
export class SnapshotsComponent implements OnInit {
  companies: SnapshotCompany[] = [];
  company = '';
  pages: SnapshotPage[] = [];
  total = 0;
  first = 0;
  rows = 10;
  loading = false;
  error = '';

  constructor(private svc: SnapshotService) {}

  ngOnInit(): void { this.loadCompanies(); }

  loadCompanies(): void {
    this.svc.listCompanies().subscribe({
      next: rows => {
        this.companies = rows;
        if (!this.company && rows[0]) { this.company = rows[0].company; this.first = 0; this.fetch(); }
      },
      error: () => this.error = 'Could not load snapshots (is data-collection-service on :8084 running?).'
    });
  }

  selected(): SnapshotCompany | undefined { return this.companies.find(c => c.company === this.company); }

  onCompanyChange(): void { this.first = 0; this.fetch(); }
  reload(): void { this.loadCompanies(); this.fetch(); }

  load(event: TableLazyLoadEvent): void {
    this.first = event.first ?? 0;
    this.rows = (event.rows as number) || this.rows;
    this.fetch();
  }

  private fetch(): void {
    if (!this.company) { this.pages = []; this.total = 0; return; }
    this.loading = true;
    this.svc.pages(this.company, this.first, this.rows).subscribe({
      next: r => { this.pages = r.pages; this.total = r.total; this.loading = false; },
      error: () => { this.error = 'Could not load snapshot pages.'; this.loading = false; }
    });
  }

  imgUrl(imageId: string): string { return this.svc.imageUrl(this.company, imageId); }
}
