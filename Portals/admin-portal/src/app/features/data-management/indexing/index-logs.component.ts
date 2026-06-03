import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ButtonModule } from 'primeng/button';
import { CompanyService } from '../../../core/company.service';
import { IndexingService, IndexLog } from '../../../core/indexing.service';
import { Company } from '../../../core/models';

@Component({
  selector: 'vkp-index-logs',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TableModule, TagModule, ButtonModule],
  template: `
  <h1 class="vkp-page-title">Data Indexing <span class="vkp-muted">› Index Logs</span></h1>
  <div class="vkp-card">
    <div class="vkp-toolbar">
      <label style="font-weight:600;">Company</label>
      <select [(ngModel)]="companyId" (ngModelChange)="load()"
              style="padding:.5rem; border:1px solid var(--vkp-border); border-radius:6px; min-width:240px;">
        <option *ngFor="let c of companies" [value]="c.companyId">{{ c.name }}</option>
      </select>
      <span class="vkp-spacer"></span>
      <a [routerLink]="['/data-management','data-indexing','trigger']"><p-button label="Trigger Indexing" [text]="true" icon="pi pi-bolt"></p-button></a>
      <p-button label="Refresh" icon="pi pi-refresh" [outlined]="true" (onClick)="load()"></p-button>
    </div>
    <div *ngIf="error" class="vkp-alert-err">{{ error }}</div>
    <p-table [value]="rows" [loading]="loading" [paginator]="rows.length > 15" [rows]="15" [tableStyle]="{ 'min-width': '64rem' }">
      <ng-template pTemplate="header">
        <tr>
          <th style="width:8rem">Status</th><th style="width:6rem">Type</th><th>Model → vector table</th>
          <th style="width:7rem">Scope</th><th style="width:5rem">Chunks</th><th>Run ref</th><th style="width:11rem">Updated</th>
        </tr>
      </ng-template>
      <ng-template pTemplate="body" let-l>
        <tr>
          <td><p-tag [value]="l.status" [severity]="statusSeverity(l.status)"></p-tag></td>
          <td><p-tag [value]="l.wfType" [severity]="l.wfType === 'AIRFLOW' ? 'info' : 'success'"></p-tag></td>
          <td><span style="font-family:monospace; font-size:.82rem">{{ l.embeddingModel }}</span>
            <div class="vkp-muted" style="font-size:.78rem">{{ l.vectorTarget }}</div></td>
          <td><p-tag [value]="(l.scope || '—') + (l.docCount ? ' (' + l.docCount + ')' : '')" severity="secondary"></p-tag></td>
          <td>{{ l.chunks ?? '—' }}</td>
          <td style="font-family:monospace; font-size:.78rem; color:var(--vkp-muted)">{{ l.runRef }}
            <div *ngIf="l.error" class="vkp-alert-err" style="margin:.3rem 0 0; font-family:inherit;">{{ l.error }}</div></td>
          <td class="vkp-muted" style="font-size:.82rem">{{ l.updatedDt | date:'short' }}</td>
        </tr>
      </ng-template>
      <ng-template pTemplate="emptymessage">
        <tr><td colspan="7" class="vkp-muted" style="text-align:center; padding:1.5rem;">No index runs yet for this company.</td></tr>
      </ng-template>
    </p-table>
  </div>
  `
})
export class IndexLogsComponent implements OnInit {
  companies: Company[] = [];
  companyId = '';
  rows: IndexLog[] = [];
  loading = false;
  error = '';

  constructor(private companySvc: CompanyService, private svc: IndexingService) {}

  ngOnInit(): void {
    this.companySvc.list().subscribe({
      next: rows => {
        this.companies = rows;
        if (rows.length && rows[0].companyId) { this.companyId = rows[0].companyId; this.load(); }
      },
      error: () => this.error = 'Could not load companies (is company-service on :8081 running?).'
    });
  }

  load(): void {
    if (!this.companyId) { this.rows = []; return; }
    this.loading = true; this.error = '';
    this.svc.logs(this.companyId).subscribe({
      next: r => { this.rows = r; this.loading = false; },
      error: () => { this.error = 'Could not load index logs (is indexing-service on :8086 running?).'; this.loading = false; }
    });
  }

  statusSeverity(s?: string): 'success' | 'info' | 'warn' | 'danger' | 'secondary' {
    switch (s) {
      case 'INDEXED': return 'success';
      case 'IN_PROGRESS': return 'info';
      case 'PENDING': return 'warn';
      case 'FAILED': return 'danger';
      default: return 'secondary';
    }
  }
}
