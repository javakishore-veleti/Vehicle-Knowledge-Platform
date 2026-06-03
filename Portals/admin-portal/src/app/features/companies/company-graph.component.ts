import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TableModule, TableLazyLoadEvent } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { CompanyService } from '../../core/company.service';
import { DiscoveryService } from '../../core/discovery.service';
import { Company, ResourceGraphNode } from '../../core/models';

@Component({
  selector: 'vkp-company-graph',
  standalone: true,
  imports: [CommonModule, FormsModule, TableModule, ButtonModule, TagModule],
  template: `
  <h1 class="vkp-page-title">Companies <span class="vkp-muted">› Resource Graph</span></h1>

  <div class="vkp-card">
    <div class="vkp-toolbar">
      <label style="font-weight:600;">Company</label>
      <select [(ngModel)]="companyId" (ngModelChange)="onCompany()"
              style="padding:.5rem; border:1px solid var(--vkp-border); border-radius:6px; min-width:240px;">
        <option *ngFor="let c of companies" [value]="c.companyId">{{ c.name }}</option>
      </select>
      <span class="vkp-muted">{{ total | number }} node(s)</span>
      <span class="vkp-spacer"></span>
      <p-button label="Refresh" icon="pi pi-refresh" [outlined]="true" (onClick)="reload()"></p-button>
    </div>

    <div *ngIf="error" class="vkp-alert-err">{{ error }}</div>

    <!-- Server-side pagination: only the visible page is fetched (graphs can be 100k+ rows). -->
    <p-table [value]="nodes" [lazy]="true" (onLazyLoad)="load($event)" [loading]="loading"
             [paginator]="true" [rows]="rows" [first]="first" [totalRecords]="total"
             [rowsPerPageOptions]="[100, 500, 1000]" [showCurrentPageReport]="true"
             currentPageReportTemplate="{first}–{last} of {totalRecords}" [tableStyle]="{ 'min-width': '56rem' }">
      <ng-template pTemplate="header">
        <tr><th style="width:9rem">Type</th><th>URL</th><th style="width:10rem">Crawl status</th></tr>
      </ng-template>
      <ng-template pTemplate="body" let-n>
        <tr>
          <td><p-tag [value]="n.resourceType || '—'" [severity]="typeSeverity(n.resourceType)"></p-tag></td>
          <td><a [href]="n.resourceUrl" target="_blank" rel="noopener" style="color:var(--vkp-brand-2);">{{ n.resourceUrl }}</a></td>
          <td><p-tag [value]="n.crawlStatus || '—'" severity="secondary"></p-tag></td>
        </tr>
      </ng-template>
      <ng-template pTemplate="emptymessage">
        <tr><td colspan="3" class="vkp-muted" style="text-align:center; padding:1.5rem;">
          No graph nodes for this company. Discovered links and registered snapshot pages appear here.
        </td></tr>
      </ng-template>
    </p-table>
  </div>
  `
})
export class CompanyGraphComponent implements OnInit {
  companies: Company[] = [];
  companyId = '';
  nodes: ResourceGraphNode[] = [];
  total = 0;
  first = 0;
  rows = 100;
  loading = false;
  error = '';

  constructor(private companySvc: CompanyService, private discoverySvc: DiscoveryService) {}

  ngOnInit(): void {
    this.companySvc.list().subscribe({
      next: rows => {
        this.companies = rows;
        if (rows.length && rows[0].companyId) { this.companyId = rows[0].companyId; this.fetch(); }
      },
      error: () => this.error = 'Could not load companies (is company-service on :8081 running?).'
    });
  }

  /** Fired by the paginator (and once on init). */
  load(event: TableLazyLoadEvent): void {
    this.first = event.first ?? 0;
    this.rows = event.rows ?? this.rows;
    if (this.companyId) { this.fetch(); }
  }

  onCompany(): void { this.first = 0; this.fetch(); }

  reload(): void { this.fetch(); }

  fetch(): void {
    if (!this.companyId) { this.nodes = []; this.total = 0; return; }
    this.loading = true; this.error = '';
    this.discoverySvc.getGraphPaged(this.companyId, this.first, this.rows).subscribe({
      next: p => { this.nodes = p.nodes; this.total = p.total; this.loading = false; },
      error: () => { this.error = 'Could not load the resource graph (is data-collection-service on :8084 running?).'; this.loading = false; }
    });
  }

  typeSeverity(t?: string): 'info' | 'success' | 'warn' | 'secondary' {
    switch (t) {
      case 'SEED': return 'info';
      case 'SNAPSHOT_PAGE': return 'success';
      case 'LINK': return 'warn';
      default: return 'secondary';
    }
  }
}
